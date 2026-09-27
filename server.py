#!/usr/bin/env python3
"""Servidor web Nexo Estudo: API JSON, autenticação e persistência SQLite."""
import hashlib, hmac, json, mimetypes, os, re, secrets, sqlite3
from datetime import date, timedelta
from http import cookies
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT=Path(__file__).parent; DB=Path(os.getenv("NEXO_DB", ROOT/"data"/"nexo.db")); SESSIONS={}
def conn():
    DB.parent.mkdir(parents=True,exist_ok=True); c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; c.execute("PRAGMA foreign_keys=ON"); return c
def init_db():
    with conn() as c:
        c.executescript("""CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,name TEXT NOT NULL,email TEXT UNIQUE NOT NULL,password_hash TEXT NOT NULL,demo INTEGER NOT NULL DEFAULT 0,created_at TEXT DEFAULT CURRENT_TIMESTAMP);CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY,user_id INTEGER NOT NULL,title TEXT NOT NULL,subject TEXT NOT NULL,due_date TEXT,prompt TEXT NOT NULL DEFAULT '',draft TEXT NOT NULL DEFAULT '',done INTEGER NOT NULL DEFAULT 0,is_example INTEGER NOT NULL DEFAULT 0,updated_at TEXT DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);""")
def password_hash(password,salt=None):
    salt=salt or secrets.token_bytes(16); digest=hashlib.scrypt(password.encode(),salt=salt,n=16384,r=8,p=1); return salt.hex()+":"+digest.hex()
def verify(password,stored):
    try:s,d=stored.split(":");return hmac.compare_digest(password_hash(password,bytes.fromhex(s)),stored)
    except (ValueError,TypeError):return False
def row_task(r): return {k:(bool(r[k]) if k in ('done','is_example') else r[k]) for k in r.keys()}
class App(BaseHTTPRequestHandler):
    server_version="NexoEstudo/1.0"
    def log_message(self,fmt,*args): print(f"{self.address_string()} - {fmt%args}")
    def json(self,status,data,extra=None):
        raw=json.dumps(data,ensure_ascii=False).encode();self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(raw)));self.send_header('Cache-Control','no-store');
        for k,v in (extra or {}).items():self.send_header(k,v)
        self.end_headers();self.wfile.write(raw)
    def body(self):
        try:return json.loads(self.rfile.read(int(self.headers.get('Content-Length','0'))) or b'{}')
        except json.JSONDecodeError:return {}
    def user(self):
        jar=cookies.SimpleCookie(self.headers.get('Cookie')); token=jar.get('nexo_session'); uid=SESSIONS.get(token.value) if token else None
        if not uid:return None
        with conn() as c:return c.execute('SELECT id,name,email,demo FROM users WHERE id=?',(uid,)).fetchone()
    def require(self):
        u=self.user()
        if not u:self.json(401,{'error':'Faça login para continuar.'})
        return u
    def do_GET(self):
        p=urlparse(self.path).path
        if p=='/':return self.file(ROOT/'index.html')
        if p.startswith('/static/'):
            target=(ROOT/p.lstrip('/')).resolve()
            if ROOT not in target.parents:return self.send_error(403)
            return self.file(target)
        if p=='/api/me':
            u=self.require();return self.json(200,dict(u)) if u else None
        if p=='/api/tasks':
            u=self.require()
            if not u:return
            with conn() as c: rows=c.execute('SELECT * FROM tasks WHERE user_id=? ORDER BY done,due_date IS NULL,due_date,id DESC',(u['id'],)).fetchall()
            return self.json(200,[row_task(r) for r in rows])
        self.send_error(404)
    def file(self,path):
        if not path.is_file():return self.send_error(404)
        data=path.read_bytes();self.send_response(200);self.send_header('Content-Type',mimetypes.guess_type(path)[0] or 'application/octet-stream');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
    def do_POST(self):
        p=urlparse(self.path).path; data=self.body()
        if p=='/api/auth/register':
            name=str(data.get('name','')).strip();email=str(data.get('email','')).strip().lower();password=str(data.get('password',''))
            if len(name)<2 or not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+',email) or len(password)<8:return self.json(400,{'error':'Confira nome, e-mail e senha (mínimo de 8 caracteres).'})
            try:
                with conn() as c: uid=c.execute('INSERT INTO users(name,email,password_hash) VALUES(?,?,?)',(name,email,password_hash(password))).lastrowid
            except sqlite3.IntegrityError:return self.json(409,{'error':'Este e-mail já possui uma conta.'})
            return self.login(uid)
        if p=='/api/auth/login':
            with conn() as c:u=c.execute('SELECT * FROM users WHERE email=?',(str(data.get('email','')).strip().lower(),)).fetchone()
            if not u or not verify(str(data.get('password','')),u['password_hash']):return self.json(401,{'error':'E-mail ou senha incorretos.'})
            return self.login(u['id'])
        if p=='/api/auth/demo':
            token=secrets.token_urlsafe(12);email=f'demo-{token}@local.invalid'
            with conn() as c:
                uid=c.execute("INSERT INTO users(name,email,password_hash,demo) VALUES(?,?,?,1)",('Visitante',email,password_hash(secrets.token_urlsafe()))).lastrowid
                today=date.today(); examples=[('Mapa mental: Ecossistemas','Biologia',today+timedelta(days=1),'Crie um mapa mental relacionando seres vivos, fatores abióticos e cadeias alimentares.'),('Lista de funções','Matemática',today+timedelta(days=3),'Resolva os exercícios de função afim e registre o raciocínio.'),('Leitura e resenha','Língua Portuguesa',today+timedelta(days=6),'Leia o conto indicado pela professora e prepare uma resenha crítica.')]
                c.executemany('INSERT INTO tasks(user_id,title,subject,due_date,prompt,is_example) VALUES(?,?,?,?,?,1)',[(uid,a,b,d.isoformat(),p) for a,b,d,p in examples])
            return self.login(uid)
        if p=='/api/auth/logout':
            jar=cookies.SimpleCookie(self.headers.get('Cookie'));token=jar.get('nexo_session');SESSIONS.pop(token.value,None) if token else None
            return self.json(200,{'ok':True},{'Set-Cookie':'nexo_session=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0'})
        if p=='/api/tasks':
            u=self.require()
            if not u:return
            title=str(data.get('title','')).strip()[:160];subject=str(data.get('subject','')).strip()[:80];due=str(data.get('due_date','')).strip() or None;prompt=str(data.get('prompt','')).strip()[:20000]
            if not title or not subject:return self.json(400,{'error':'Título e disciplina são obrigatórios.'})
            if due:
                try:date.fromisoformat(due)
                except ValueError:return self.json(400,{'error':'Data inválida.'})
            with conn() as c:tid=c.execute('INSERT INTO tasks(user_id,title,subject,due_date,prompt,is_example) VALUES(?,?,?,?,?,?)',(u['id'],title,subject,due,prompt,int(bool(data.get('is_example'))))).lastrowid;r=c.execute('SELECT * FROM tasks WHERE id=?',(tid,)).fetchone()
            return self.json(201,row_task(r))
        self.send_error(404)
    def login(self,uid):
        token=secrets.token_urlsafe(32);SESSIONS[token]=uid;return self.json(200,{'ok':True},{'Set-Cookie':f'nexo_session={token}; Path=/; HttpOnly; SameSite=Lax; Max-Age=86400'})
    def do_PATCH(self):return self.update_task(False)
    def do_PUT(self):return self.update_task(True)
    def update_task(self,draft_only):
        p=urlparse(self.path).path;m=re.fullmatch(r'/api/tasks/(\d+)(/draft)?',p);u=self.require()
        if not u:return
        if not m:return self.send_error(404)
        data=self.body();tid=int(m.group(1))
        with conn() as c:
            found=c.execute('SELECT * FROM tasks WHERE id=? AND user_id=?',(tid,u['id'])).fetchone()
            if not found:return self.json(404,{'error':'Tarefa não encontrada.'})
            if draft_only or m.group(2):c.execute("UPDATE tasks SET draft=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",(str(data.get('draft',''))[:50000],tid))
            else:c.execute("UPDATE tasks SET done=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",(int(bool(data.get('done'))),tid))
            r=c.execute('SELECT * FROM tasks WHERE id=?',(tid,)).fetchone()
        return self.json(200,row_task(r))
    def do_DELETE(self):
        m=re.fullmatch(r'/api/tasks/(\d+)',urlparse(self.path).path);u=self.require()
        if not u:return
        if not m:return self.send_error(404)
        with conn() as c:cur=c.execute('DELETE FROM tasks WHERE id=? AND user_id=?',(int(m.group(1)),u['id']))
        return self.json(200,{'ok':bool(cur.rowcount)})
if __name__=='__main__':
    init_db();port=int(os.getenv('PORT','8000'));print(f'Nexo Estudo em http://localhost:{port}');ThreadingHTTPServer(('0.0.0.0',port),App).serve_forever()
