"""Local SiliconOS workbench. Run: python3 server.py. Not a public production server."""
import json
import os
import re
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse
from siliconos import ai
from siliconos.engine import explore, simulate

ROOT=Path(__file__).resolve().parent
DB=ROOT/"data"/"siliconos.db"
RUN_LOCK=threading.Lock()

def connect():
    DB.parent.mkdir(exist_ok=True)
    db=sqlite3.connect(DB)
    db.execute("CREATE TABLE IF NOT EXISTS runs (id TEXT PRIMARY KEY, payload TEXT NOT NULL)")
    db.execute("CREATE TABLE IF NOT EXISTS events (at TEXT, name TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS pilots (email TEXT PRIMARY KEY, created_at TEXT, payload TEXT)")
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
            return self.reply(200,dict(ai=ai.configured(),simulator=bool(shutil.which("iverilog") and shutil.which("vvp")),board=False))
        if path=="/api/runs":
            with connect() as db: rows=db.execute("SELECT payload FROM runs ORDER BY rowid DESC LIMIT 20").fetchall()
            return self.reply(200,[json.loads(r[0]) for r in rows])
        if path.startswith("/api/runs/"):
            with connect() as db: row=db.execute("SELECT payload FROM runs WHERE id=?",(path.rsplit("/",1)[-1],)).fetchone()
            return self.reply(200,json.loads(row[0])) if row else self.reply(404,{"error":"Run not found"})
        files={"/":("index.html","text/html"),"/app.js":("app.js","application/javascript"),"/style.css":("style.css","text/css")}
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
            if not 0<length<=16384: raise ValueError("Invalid request size")
            data=json.loads(self.rfile.read(length))
            if not isinstance(data,dict): raise ValueError("Request must be an object")
            path=urlparse(self.path).path
            if path=="/api/explore": result=explore(data.get("spec"))
            elif path=="/api/spec": result=ai.generate(data.get("prompt"))
            elif path=="/api/pilot": result=save_pilot(data)
            elif path=="/api/simulate":
                if not RUN_LOCK.acquire(blocking=False): return self.reply(409,{"error":"A simulation is already running. Try again shortly."})
                try: result=simulate(data.get("spec"),data.get("lanes"),data.get("seed",42))
                finally: RUN_LOCK.release()
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
