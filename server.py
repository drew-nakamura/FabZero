"""Local SiliconOS workbench. Run: python3 server.py. Not a public production server."""
import hashlib
import json
import os
import re
import shutil
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse
from siliconos import ai, rtlgen, catalog, handoff, board, fpga
from siliconos.engine import explore, simulate, validate

ROOT=Path(__file__).resolve().parent
DB=ROOT/"data"/"siliconos.db"
BOARD_CHECK=ROOT/"hw"/"matmul_board"/"results"/"board_check.json"
RUN_LOCK=threading.Lock()
BOARD_LOCK=threading.Lock()
BOARD_CHECK_LOCK=threading.Lock()

class _Connection(sqlite3.Connection):
    """`with connect() as db:` commits/rolls back as before, then closes the file
    (an unclosed SQLite file stays locked on Windows)."""
    def __exit__(self,*exc):
        try: return super().__exit__(*exc)
        finally: self.close()

def connect():
    DB.parent.mkdir(exist_ok=True)
    db=sqlite3.connect(DB,factory=_Connection)
    db.execute("CREATE TABLE IF NOT EXISTS runs (id TEXT PRIMARY KEY, payload TEXT NOT NULL)")
    db.execute("CREATE TABLE IF NOT EXISTS events (at TEXT, name TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS pilots (email TEXT PRIMARY KEY, created_at TEXT, payload TEXT)")
    return db

def now(): return datetime.now(timezone.utc).isoformat()

def import_board_result(parent_id,envelope):
    """Verify a signed KV260 result and save it as a separate board_measured child run.
    Idempotent on runner_result_id; the parent run is never modified."""
    with BOARD_LOCK:
        with connect() as db: row=db.execute("SELECT payload FROM runs WHERE id=?",(parent_id,)).fetchone()
        if not row: raise LookupError("Parent run not found")
        wrapper=hashlib.sha256((ROOT/"hardware"/"matmul_axi.sv").read_bytes()).hexdigest()
        child=board.accept(json.loads(row[0]),envelope,wrapper)
        with connect() as db:
            for (payload,) in db.execute("SELECT payload FROM runs WHERE payload LIKE ?",('%"board_measured"%',)):
                existing=json.loads(payload)
                if existing.get("runner_result_id")==child["runner_result_id"]:
                    return {**existing,"already_imported":True}
            db.execute("INSERT INTO runs VALUES (?,?)",(child["id"],json.dumps(child)))
            db.execute("INSERT INTO events VALUES (?,?)",(now(),"/api/runs/board-result"))
        return child

def save_pilot(data):
    if data.get('consent') is not True:
        raise ValueError('Please consent to follow-up for this student prototype.')
    clean={}
    for field in ('email','role','platform','challenge','organization','tools'):
        value=data.get(field,'')
        if not isinstance(value,str) or len(value)>1000:
            raise ValueError('Invalid '+field)
        clean[field]=value.strip()
    if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',clean['email']) or len(clean['email'])>254:
        raise ValueError('Enter a valid email address.')
    if not all(clean[k] for k in ('role','platform','challenge')):
        raise ValueError('Role, platform, and engineering challenge are required.')
    clean['consent']=True
    with connect() as db:
        db.execute('INSERT OR REPLACE INTO pilots VALUES (?,?,?)',(clean['email'].lower(),now(),json.dumps(clean)))
    return {'saved':True}

class Handler(BaseHTTPRequestHandler):
    def reply(self,status,payload):
        body=json.dumps(payload).encode()
        self.send_response(status); self.send_header("Content-Type","application/json")
        self.send_header("Cache-Control","no-store"); self.send_header("Content-Length",str(len(body)))
        self.end_headers(); self.wfile.write(body)

    def send_file(self,body,mime):
        self.send_response(200); self.send_header("Content-Type",mime); self.send_header("Cache-Control","no-store")
        self.send_header("X-Content-Type-Options","nosniff"); self.send_header("Content-Length",str(len(body)))
        self.end_headers(); self.wfile.write(body)

    def load_run(self,run_id):
        with connect() as db: row=db.execute("SELECT payload FROM runs WHERE id=?",(run_id,)).fetchone()
        return json.loads(row[0]) if row else None

    def do_GET(self):
        path=urlparse(self.path).path
        if path=="/api/status":
            board_details=board.board_status(BOARD_CHECK)
            return self.reply(200,dict(ai=ai.configured(),ai_details=ai.details(),simulator=bool(shutil.which("iverilog") and shutil.which("vvp")),board=board_details["available"],board_details=board_details))
        if path=="/api/fpga/builds":
            return self.reply(200,{"builds":[fpga.build_evidence(lanes) for lanes in (1,4)]})
        match=re.fullmatch(r'/api/fpga/builds/([14])/reports/([a-z_]+\.(?:rpt|txt))',path)
        if match:
            try: return self.send_file(fpga.report_text(int(match.group(1)),match.group(2)),"text/plain; charset=utf-8")
            except LookupError as error: return self.reply(404,{"error":str(error)})
            except ValueError as error: return self.reply(409,{"error":str(error)})
        match=re.fullmatch(r'/api/board/jobs/([a-f0-9-]{36})',path)
        if match:
            job=fpga.get_job(match.group(1))
            return self.reply(200,job) if job else self.reply(404,{"error":"Board job not found"})
        match=re.fullmatch(r'/api/board/results/([^/]+)/([a-z.-]+)',path)
        if match:
            try: return self.send_file(*fpga.result_file(match.group(1),match.group(2)))
            except LookupError as error: return self.reply(404,{"error":str(error)})
        match=re.fullmatch(r'/api/runs/([a-f0-9-]{36})/handoff.json',path)
        if match:
            run=self.load_run(match.group(1))
            if not run: return self.reply(404,{"error":"Run not found"})
            try: return self.reply(200,fpga.handoff_contents(run))
            except (ValueError,TypeError,KeyError): return self.reply(400,{"error":"This run lacks valid handoff evidence."})
        if path=="/api/catalog":
            return self.reply(200,{"blocks":catalog.blocks()})
        if path=="/api/runs":
            with connect() as db: rows=db.execute("SELECT payload FROM runs ORDER BY rowid DESC LIMIT 20").fetchall()
            heavy={'source_files','netlist_verilog','netlist_testbench','synthesis_log','verification_log','simulator_stdout','statistics','synthesis','build_recipe'}
            return self.reply(200,[{k:v for k,v in json.loads(r[0]).items() if k not in heavy} for r in rows])
        match=re.fullmatch(r'/api/runs/([a-f0-9-]{36})/handoff.zip',path)
        if match:
            with connect() as db: row=db.execute("SELECT payload FROM runs WHERE id=?",(match.group(1),)).fetchone()
            if not row: return self.reply(404,{"error":"Run not found"})
            try: body=handoff.archive(json.loads(row[0]))
            except (ValueError,TypeError,KeyError):
                return self.reply(400,{"error":"This run lacks valid handoff evidence. Create a new verified run."})
            self.send_response(200)
            self.send_header('Content-Type','application/zip')
            self.send_header('Content-Disposition','attachment; filename="siliconos-'+match.group(1)+'-handoff.zip"')
            self.send_header('Content-Length',str(len(body)))
            self.send_header('Cache-Control','no-store')
            self.end_headers();self.wfile.write(body)
            return
        if path.startswith("/api/runs/"):
            run=self.load_run(path.rsplit("/",1)[-1])
            if not run: return self.reply(404,{"error":"Run not found"})
            if run.get("evidence")=="board_measured" and not run.get("runner_result_folder"):
                run["runner_result_folder"]=fpga.find_result_folder(run.get("runner_result_id"))
            return self.reply(200,run)
        files={"/":("index.html","text/html"),"/app.js":("app.js","application/javascript"),"/pipeline.js":("pipeline.js","application/javascript"),"/catalog.js":("catalog.js","application/javascript"),"/style.css":("style.css","text/css")}
        if path not in files: return self.reply(404,{"error":"Not found"})
        name,mime=files[path]; body=(ROOT/"web"/name).read_bytes()
        self.send_response(200); self.send_header("Content-Type",mime); self.send_header("Content-Length",str(len(body)))
        self.send_header("X-Content-Type-Options","nosniff"); self.end_headers(); self.wfile.write(body)

    def do_POST(self):
        origin=self.headers.get("Origin")
        if origin and origin not in (f"http://localhost:{self.server.server_port}",f"http://127.0.0.1:{self.server.server_port}"):
            return self.reply(403,{"error":"Cross-origin requests are not accepted."})
        try:
            path=urlparse(self.path).path
            board_route=re.fullmatch(r'/api/runs/([a-f0-9-]{36})/board-result',path)
            length=int(self.headers.get("Content-Length","0"))
            # A signed board result carries its implementation manifest and summary.
            if not 0<length<=(524288 if board_route else 16384): raise ValueError("Invalid request size")
            data=json.loads(self.rfile.read(length))
            if not isinstance(data,dict): raise ValueError("Request must be an object")
            if board_route:
                try: return self.reply(200,import_board_result(board_route.group(1),data))
                except LookupError as error: return self.reply(404,{"error":str(error)})
            run_route=re.fullmatch(r'/api/runs/([a-f0-9-]{36})/board-run',path)
            if run_route:
                run=self.load_run(run_route.group(1))
                if not run: return self.reply(404,{"error":"Run not found"})
                return self.reply(200,fpga.start_board_run(run,import_board_result))
            if path=="/api/board/check":
                if not BOARD_CHECK_LOCK.acquire(blocking=False): return self.reply(409,{"error":"A board check is already running."})
                try: return self.reply(200,fpga.check_board(BOARD_CHECK))
                finally: BOARD_CHECK_LOCK.release()
            if path=="/api/explore": result=explore(data.get("spec"))
            elif path=="/api/spec": result=ai.generate(data.get("prompt"),data.get("target"))
            elif path=="/api/plan": result=catalog.plan(data.get("spec"),data.get("lanes"),data.get("block_id"))
            elif path=="/api/pilot": result=save_pilot(data)
            elif path=="/api/build":
                if not RUN_LOCK.acquire(blocking=False): return self.reply(409,{"error":"A hardware tool run is already active. Try again shortly."})
                try:
                    recipe=catalog.plan(data.get('spec'),data.get('lanes'),data.get('block_id'))
                    spec=recipe['spec']; lanes=recipe['parameters']['LANES']
                    result=simulate(spec,lanes,42)
                    expected={Path(k).name:v for k,v in recipe['source_sha256'].items()}
                    if result['source_sha256']!=expected:
                        raise ValueError('Sources changed during the build. Retry with a fresh recipe.')
                    result.update(build_recipe=recipe,id=str(uuid.uuid4()),created_at=now())
                    with connect() as db:
                        db.execute('INSERT INTO runs VALUES (?,?)',(result['id'],json.dumps(result)))
                        db.execute('INSERT INTO events VALUES (?,?)',(now(),path))
                finally: RUN_LOCK.release()
                return self.reply(200,result)
            elif path=="/api/generate-rtl":
                if not RUN_LOCK.acquire(blocking=False): return self.reply(409,{"error":"A hardware tool run is already active. Try again shortly."})
                try:
                    spec=validate(data.get('spec'))
                    prompt=data.get('prompt')
                    if not isinstance(prompt,str) or not 1<=len(prompt.strip())<=4000:
                        raise ValueError('Enter a request of 1–4000 characters.')
                    # The objective selects a supported lane count, not a proven optimum for new RTL.
                    lanes=data.get('lanes',1 if spec['objective']=='minimize_lanes' else spec['max_lanes'])
                    seed=data.get('seed',42)
                    if type(lanes) is not int or lanes not in (1,4) or lanes>spec['max_lanes']:
                        raise ValueError('Candidate exceeds the lane limit or is unsupported.')
                    if type(seed) is not int or not 0<=seed<=2**31-1:
                        raise ValueError('Seed must be an integer between 0 and 2147483647.')
                    missing=[name for name in ('iverilog','vvp') if not shutil.which(name)]
                    if missing: raise ValueError('RTL generation and verification require: '+', '.join(missing))
                    source=ai.generate_rtl(spec,prompt)
                    rtlgen.gate(source)
                    result=simulate(spec,lanes,seed,source_override=source)
                    result.update(id=str(uuid.uuid4()),created_at=now(),prompt=prompt)
                    # Commit the whole pipeline and its event atomically; no partial RTL run.
                    with connect() as db:
                        db.execute('INSERT INTO runs VALUES (?,?)',(result['id'],json.dumps(result)))
                        db.execute('INSERT INTO events VALUES (?,?)',(now(),path))
                finally: RUN_LOCK.release()
                return self.reply(200,result)
            elif path=="/api/simulate":
                if not RUN_LOCK.acquire(blocking=False): return self.reply(409,{"error":"A hardware tool run is already active. Try again shortly."})
                try:
                    result=simulate(data.get("spec"),data.get("lanes"),data.get("seed",42))
                finally: RUN_LOCK.release()
                result["build_recipe"]=catalog.plan(result["spec"],result["lanes"])
                result.update(id=str(uuid.uuid4()),created_at=now())
                with connect() as db: db.execute("INSERT INTO runs VALUES (?,?)",(result["id"],json.dumps(result)))
            else: return self.reply(404,{"error":"Not found"})
            with connect() as db: db.execute("INSERT INTO events VALUES (?,?)",(now(),path))
            self.reply(200,result)
        except (ValueError,TypeError,KeyError) as error: self.reply(400,{"error":str(error)})
        except Exception:
            self.reply(502,{"error":"The service could not complete this request. Check tool/API availability and retry. No result was accepted."})

if __name__=="__main__":
    port=int(os.environ.get("PORT","8000"))
    print(f"SiliconOS http://127.0.0.1:{port}",flush=True)
    ThreadingHTTPServer(("127.0.0.1",port),Handler).serve_forever()
