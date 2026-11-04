import os, sqlite3, secrets, uuid, hmac
from pathlib import Path
from datetime import timedelta
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

ROOT = Path(__file__).resolve().parent
DATA = Path(os.getenv('DATA_DIR', str(ROOT / 'data')))
DATA.mkdir(parents=True, exist_ok=True)
UPLOAD = DATA / 'uploads'
UPLOAD.mkdir(exist_ok=True)
DB = DATA / 'radio.sqlite3'
app = Flask(__name__)
app.config.update(SECRET_KEY=os.environ.get('SECRET_KEY', secrets.token_hex(32)), MAX_CONTENT_LENGTH=25*1024*1024, SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax', SESSION_COOKIE_SECURE=os.getenv('COOKIE_SECURE')=='1', PERMANENT_SESSION_LIFETIME=timedelta(hours=8))
EXT = {'jpg':'image/jpeg','jpeg':'image/jpeg','png':'image/png','webp':'image/webp','gif':'image/gif','mp3':'audio/mpeg','ogg':'audio/ogg','wav':'audio/wav','mp4':'video/mp4','webm':'video/webm'}

def conn():
    c=sqlite3.connect(DB)
    c.row_factory=sqlite3.Row
    return c

def init():
    with conn() as c:
        c.execute('CREATE TABLE IF NOT EXISTS posts (id TEXT PRIMARY KEY, type TEXT NOT NULL, title TEXT NOT NULL, description TEXT NOT NULL, image TEXT, media TEXT, created TEXT DEFAULT CURRENT_TIMESTAMP)')
        c.execute('CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL)')
        c.execute('CREATE TABLE IF NOT EXISTS admins (id INTEGER PRIMARY KEY, password_hash TEXT NOT NULL)')
        if not c.execute('SELECT id FROM admins WHERE id=1').fetchone():
            password=os.environ.get('ADMIN_PASSWORD')
            if not password or len(password)<12:
                raise RuntimeError('Set ADMIN_PASSWORD to a unique password of at least 12 characters before starting.')
            c.execute('INSERT INTO admins(id,password_hash) VALUES(1,?)',(generate_password_hash(password),))
init()

def csrf():
    if 'csrf' not in session: session['csrf']=secrets.token_urlsafe(32)
    return session['csrf']

def protected(fn):
    @wraps(fn)
    def wrapped(*args,**kwargs):
        if not session.get('admin'): return jsonify(error='Login required'),401
        if not hmac.compare_digest(request.headers.get('X-CSRF-Token',''),csrf()): return jsonify(error='Invalid security token'),403
        return fn(*args,**kwargs)
    return wrapped

@app.after_request
def headers(resp):
    resp.headers['X-Content-Type-Options']='nosniff'
    resp.headers['Referrer-Policy']='strict-origin-when-cross-origin'
    resp.headers['X-Frame-Options']='DENY'
    resp.headers['Content-Security-Policy'] = "default-src 'self'; img-src 'self' data: https:; media-src 'self' https:; style-src 'self' 'unsafe-inline' https:; script-src 'self' https://cdn.cloud.caster.fm; connect-src 'self' https:; frame-src https://widgets.cloud.caster.fm; base-uri 'self'; object-src 'none'; frame-ancestors 'none'"
    return resp

@app.get('/')
def home(): return render_template('index.html')

@app.get('/api/status')
def status(): return jsonify(admin=bool(session.get('admin')),csrf=csrf() if session.get('admin') else None)

@app.post('/api/login')
def login():
    pw=(request.get_json(silent=True) or {}).get('password','')
    with conn() as c: row=c.execute('SELECT password_hash FROM admins WHERE id=1').fetchone()
    if not isinstance(pw,str) or not check_password_hash(row['password_hash'],pw): return jsonify(error='Wrong password'),401
    session.clear();session.permanent=True;session['admin']=True
    return jsonify(ok=True,csrf=csrf())

@app.post('/api/logout')
@protected
def logout(): session.clear();return jsonify(ok=True)

@app.get('/api/posts')
def posts():
    with conn() as c: rows=c.execute('SELECT * FROM posts ORDER BY created DESC, rowid DESC LIMIT 500').fetchall()
    return jsonify([dict(r) for r in rows])

@app.post('/api/posts')
@protected
def add_post():
    kind=request.form.get('type','');title=request.form.get('title','').strip();desc=request.form.get('description','').strip();media=request.form.get('media','').strip()
    if kind not in ('news','photo','video','program') or not (1<=len(title)<=120) or len(desc)>10000: return jsonify(error='Invalid fields'),400
    if media and (not media.startswith('https://') or len(media)>2000): return jsonify(error='HTTPS media link required'),400
    image=''
    f=request.files.get('image')
    if f and f.filename:
        extension=secure_filename(f.filename).rsplit('.',1)[-1].lower()
        if extension not in EXT: return jsonify(error='Unsupported file type'),400
        if f.mimetype != EXT[extension] and not (extension=='jpg' and f.mimetype=='image/jpg'): return jsonify(error='File MIME mismatch'),400
        # File signatures provide a minimal validation beyond the extension and client MIME.
        header=f.stream.read(16);f.stream.seek(0)
        valid={'jpg':header.startswith(b'\xff\xd8\xff'),'jpeg':header.startswith(b'\xff\xd8\xff'),'png':header.startswith(b'\x89PNG\r\n\x1a\n'),'webp':header.startswith(b'RIFF') and header[8:12]==b'WEBP','gif':header.startswith((b'GIF87a',b'GIF89a')),'mp3':header.startswith(b'ID3') or (len(header)>1 and header[0]==255 and (header[1]&224)==224),'ogg':header.startswith(b'OggS'),'wav':header.startswith(b'RIFF') and header[8:12]==b'WAVE','mp4':header[4:8]==b'ftyp','webm':header.startswith(b'\x1a\x45\xdf\xa3')}
        if not valid[extension]: return jsonify(error='Invalid file content'),400
        name=uuid.uuid4().hex+'.'+extension
        f.save(UPLOAD/name)
        image='/uploads/'+name
    pid=uuid.uuid4().hex
    with conn() as c:c.execute('INSERT INTO posts(id,type,title,description,image,media) VALUES(?,?,?,?,?,?)',(pid,kind,title,desc,image,media))
    return jsonify(ok=True,id=pid),201

@app.delete('/api/posts/<pid>')
@protected
def delete_post(pid):
    with conn() as c:
        row=c.execute('SELECT image FROM posts WHERE id=?',(pid,)).fetchone()
        if not row:return jsonify(error='Not found'),404
        c.execute('DELETE FROM posts WHERE id=?',(pid,))
    if row['image'] and row['image'].startswith('/uploads/'):
        (UPLOAD/Path(row['image']).name).unlink(missing_ok=True)
    return jsonify(ok=True)

@app.get('/api/settings')
def settings():
    with conn() as c: row=c.execute("SELECT value FROM settings WHERE key='stream'").fetchone()
    return jsonify(stream=row['value'] if row else '')

@app.post('/api/settings')
@protected
def save_settings():
    value=(request.get_json(silent=True) or {}).get('stream','')
    if not isinstance(value,str) or len(value)>2000 or (value and not value.startswith('https://')):return jsonify(error='HTTPS URL required'),400
    with conn() as c:c.execute("INSERT INTO settings(key,value) VALUES('stream',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",(value,))
    return jsonify(ok=True)

@app.get('/uploads/<name>')
def uploaded(name):
    if not name or '/' in name:return '',404
    resp=send_from_directory(UPLOAD,name)
    resp.headers['Cache-Control']='public, max-age=3600'
    return resp

@app.get('/health')
def health():return jsonify(ok=True)

if __name__=='__main__':
    app.run(host='127.0.0.1',port=int(os.getenv('PORT','5000')),debug=False)
