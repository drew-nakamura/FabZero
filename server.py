"""Local SiliconOS workbench. Run: python3 server.py. Not a public production server."""
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
from siliconos import ai, asic, rtlgen, catalog, handoff, board as board_evidence
from siliconos.engine import explore, simulate, validate

ROOT=Path(__file__).resolve().parent
DB=ROOT/"data"/"siliconos.db"
RUN_LOCK=threading.Lock()

def connect():
    DB.parent.mkdir(exist_ok=True)
    db=sqlite3.connect(DB)
    db.execute("CREATE TABLE IF NOT EXISTS runs (id TEXT PRIMARY KEY, payload TEXT NOT NULL)")
    db.execute("CREATE TABLE IF NOT EXISTS events (at TEXT, name TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS pilots (email TEXT PRIMARY KEY, created_at TEXT, payload TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS board_results (runner_result_id TEXT PRIMARY KEY, run_id TEXT UNIQUE NOT NULL, parent_run_id TEXT NOT NULL)")
    return db

def now(): return datetime.now(timezone.utc).isoformat()

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

    def do_GET(self):
        path=urlparse(self.path).path
        if path=="/api/status":
            import shutil
            with connect() as db:
                recorded_board_results=bool(db.execute("SELECT 1 FROM board_results LIMIT 1").fetchone())
            return self.reply(200,dict(ai=ai.configured(),simulator=bool(shutil.which("iverilog") and shutil.which("vvp")),board=False,board_recorded=recorded_board_results,asic_synthesis=bool(shutil.which("yosys") and shutil.which("iverilog") and shutil.which("vvp"))))
        if path=="/api/kv260/builds":
            from siliconos.build_compare import compare_builds
            try:
                return self.reply(200,compare_builds())
            except FileNotFoundError:
                return self.reply(404,{"error":"Build artifacts unavailable. Expected build/drew-branch/n8_l1 and n8_l4 with implementation manifests and reports."})
            except (ValueError,KeyError,TypeError,UnicodeError) as exc:
                return self.reply(409,{"error":"Build comparison rejected: "+str(exc)})
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
            with connect() as db: row=db.execute("SELECT payload FROM runs WHERE id=?",(path.rsplit("/",1)[-1],)).fetchone()
            return self.reply(200,json.loads(row[0])) if row else self.reply(404,{"error":"Run not found"})
        files={"/kv260-builds.js":("kv260-builds.js","application/javascript"),"/":("index.html","text/html"),"/app.js":("app.js","application/javascript"),"/catalog.js":("catalog.js","application/javascript"),"/progress.js":("progress.js","application/javascript"),"/style.css":("style.css","text/css")}
        if path not in files: return self.reply(404,{"error":"Not found"})
        name,mime=files[path]; body=(ROOT/"web"/name).read_bytes()
        self.send_response(200); self.send_header("Content-Type",mime); self.send_header("Content-Length",str(len(body)))
        self.send_header("X-Content-Type-Options","nosniff"); self.end_headers(); self.wfile.write(body)

    def do_POST(self):
        origin=self.headers.get("Origin")
        if origin and origin not in (f"http://localhost:{self.server.server_port}",f"http://127.0.0.1:{self.server.server_port}"):
            return self.reply(403,{"error":"Cross-origin requests are not accepted."})
        try:
            length=int(self.headers.get("Content-Length","0"))
            path=urlparse(self.path).path
            limit=262144 if path=="/api/vivado/utilization" else 16384
            if not 0<length<=limit: raise ValueError("Invalid request size")
            data=json.loads(self.rfile.read(length))
            if not isinstance(data,dict): raise ValueError("Request must be an object")
            if path=="/api/vivado/utilization":
                from siliconos.vivado import parse_import
                return self.reply(200,parse_import(data.get("report"),data.get("metadata")))
            if path=="/api/architecture-map":
                return self.reply(200,ai.generate_architecture_map(data.get("spec")))
            board_match=re.fullmatch(r'/api/runs/([a-f0-9-]{36})/board-result',path)
            if board_match:
                parent_id=board_match.group(1)
                with connect() as db:
                    row=db.execute("SELECT payload FROM runs WHERE id=?",(parent_id,)).fetchone()
                if not row: return self.reply(404,{"error":"Parent run not found"})
                result=board_evidence.validate_result(json.loads(row[0]),data)
                with connect() as db:
                    db.execute("BEGIN IMMEDIATE")
                    existing=db.execute("SELECT run_id FROM board_results WHERE runner_result_id=?",(result['runner_result_id'],)).fetchone()
                    if existing:
                        stored=db.execute("SELECT payload FROM runs WHERE id=?",(existing[0],)).fetchone()
                        if not stored: raise ValueError("Stored board result index is invalid.")
                        stored_result=json.loads(stored[0])
                        if stored_result.get('runner_payload_sha256')!=result['runner_payload_sha256']:
                            raise ValueError("runner_result_id was already used for different evidence.")
                        return self.reply(200,stored_result)
                    result.update(id=str(uuid.uuid4()),created_at=now())
                    db.execute('INSERT INTO runs VALUES (?,?)',(result['id'],json.dumps(result)))
                    db.execute('INSERT INTO board_results VALUES (?,?,?)',(result['runner_result_id'],result['id'],parent_id))
                    db.execute('INSERT INTO events VALUES (?,?)',(now(),path))
                return self.reply(200,result)
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
                    if spec['target']=='asic':
                        synthesis=asic.synthesize(spec,lanes)
                        if synthesis['source_sha256']!=expected:
                            raise ValueError('Sources changed between verification and synthesis. No build accepted.')
                        result['synthesis']=synthesis
                        result['synthesis_verified']=True
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
                    if type(lanes) is not int or lanes not in (1,2,4) or lanes>spec['max_lanes']:
                        raise ValueError('Candidate exceeds the lane limit or is unsupported.')
                    if type(seed) is not int or not 0<=seed<=2**31-1:
                        raise ValueError('Seed must be an integer between 0 and 2147483647.')
                    required=('iverilog','vvp','yosys') if spec['target']=='asic' else ('iverilog','vvp')
                    missing=[name for name in required if not shutil.which(name)]
                    if missing: raise ValueError('RTL generation and verification require: '+', '.join(missing))
                    source=ai.generate_rtl(spec,prompt)
                    rtlgen.gate(source)
                    try:
                        result=simulate(spec,lanes,seed,source_override=source)
                        attempts=1
                    except ValueError as first_failure:
                        # A single bounded repair improves useful AI iteration without
                        # persisting or displaying an unverified first candidate.
                        source=ai.repair_rtl(spec,prompt,source,str(first_failure))
                        rtlgen.gate(source)
                        result=simulate(spec,lanes,seed,source_override=source)
                        attempts=2
                    if spec['target']=='asic':
                        result['synthesis']=asic.synthesize(spec,lanes,source_override=source)
                        result['synthesis_verified']=True
                    result.update(id=str(uuid.uuid4()),created_at=now(),prompt=prompt,generation_attempts=attempts)
                    # Commit the whole pipeline and its event atomically; no partial RTL run.
                    with connect() as db:
                        db.execute('INSERT INTO runs VALUES (?,?)',(result['id'],json.dumps(result)))
                        db.execute('INSERT INTO events VALUES (?,?)',(now(),path))
                finally: RUN_LOCK.release()
                return self.reply(200,result)
            elif path in ("/api/simulate","/api/asic/synthesize"):
                if not RUN_LOCK.acquire(blocking=False): return self.reply(409,{"error":"A hardware tool run is already active. Try again shortly."})
                try:
                    result=(asic.synthesize(data.get("spec"),data.get("lanes")) if path=="/api/asic/synthesize" else simulate(data.get("spec"),data.get("lanes"),data.get("seed",42)))
                finally: RUN_LOCK.release()
                result["build_recipe"]=catalog.plan(result["spec"],result["lanes"])
                result.update(id=str(uuid.uuid4()),created_at=now())
                with connect() as db: db.execute("INSERT INTO runs VALUES (?,?)",(result["id"],json.dumps(result)))
            else: return self.reply(404,{"error":"Not found"})
            with connect() as db: db.execute("INSERT INTO events VALUES (?,?)",(now(),path))
            self.reply(200,result)
        except (ValueError,TypeError,KeyError) as error:
            # These messages are deliberately sanitized by the validation/provider layers.
            # Keep them in the local console so a rejected AI RTL candidate is diagnosable.
            print(f"Rejected {path}: {error}", flush=True)
            self.reply(400,{"error":str(error)})
        except Exception:
            self.reply(502,{"error":"The service could not complete this request. Check tool/API availability and retry. No result was accepted."})

if __name__=="__main__":
    port=int(os.environ.get("PORT","8000"))
    print(f"SiliconOS http://127.0.0.1:{port}",flush=True)
    ThreadingHTTPServer(("127.0.0.1",port),Handler).serve_forever()
