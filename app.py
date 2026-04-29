import os
import shutil
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'athl_v54_ultra'

# CHANGE YOUR CREDENTIALS TO WHATEVER YOU LIKE, BUT REMEMBER TO USE A STRONG PIN!
AUTH_USER = "ADMIN"
AUTH_PIN = "1234"

BASE_DIR = os.getcwd()
NOTES_DIR = os.path.join(BASE_DIR, 'notes')
TRASH_DIR = os.path.join(BASE_DIR, 'trash')

for d in [NOTES_DIR, TRASH_DIR]:
    if not os.path.exists(d): 
        os.makedirs(d)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login')
def login():
    if 'logged_in' in session:
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    if data.get('user') == AUTH_USER and data.get('pin') == AUTH_PIN:
        session['logged_in'] = True
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "denied"}), 401

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/api/tree')
@login_required
def get_tree():
    def build_tree(path):
        name = os.path.basename(path)
        node = {
            "name": name if name else "ROOT",
            "path": os.path.relpath(path, NOTES_DIR).replace("\\", "/"),
            "type": "dir" if os.path.isdir(path) else "file",
            "children": []
        }
        if node["type"] == "dir":
            try:
                items = sorted(os.listdir(path), key=lambda x: (not os.path.isdir(os.path.join(path, x)), x.lower()))
                for item in items:
                    node["children"].append(build_tree(os.path.join(path, item)))
            except PermissionError: pass
        else:
            node["date"] = datetime.fromtimestamp(os.path.getmtime(path)).strftime('%d.%m.%y')
        return node
    return jsonify(build_tree(NOTES_DIR))

@app.route('/get_content', methods=['POST'])
@login_required
def get_content():
    path = os.path.join(NOTES_DIR, request.json['path'].lstrip('/'))
    if os.path.exists(path) and os.path.isfile(path):
        with open(path, 'r', encoding='utf-8') as f: 
            return jsonify({"content": f.read()})
    return jsonify({"content": ""})

@app.route('/save', methods=['POST'])
@login_required
def save():
    data = request.json
    full_path = os.path.join(NOTES_DIR, data['path'].lstrip('/'))
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f: 
        f.write(data['content'])
    return jsonify({"status": "success"})

@app.route('/create', methods=['POST'])
@login_required
def create():
    data = request.json
    full_path = os.path.join(NOTES_DIR, data['name'].lstrip('/'))
    if data['type'] == 'dir':
        os.makedirs(full_path, exist_ok=True)
    else:
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        if not full_path.lower().endswith('.txt'): 
            full_path += '.txt'
        with open(full_path, 'w', encoding='utf-8') as f: 
            f.write("")
    return jsonify({"status": "success"})

@app.route('/rename', methods=['POST'])
@login_required
def rename():
    data = request.json
    old_p = os.path.join(NOTES_DIR, data['old'].lstrip('/'))
    new_p = os.path.join(os.path.dirname(old_p), data['new'])
    if os.path.exists(old_p): 
        os.rename(old_p, new_p)
    return jsonify({"status": "success"})

@app.route('/move', methods=['POST'])
@login_required
def move():
    data = request.json
    src = os.path.join(NOTES_DIR, data['src'].lstrip('/'))
    dest_folder = data['dest_folder'] if data['dest_folder'] != "ROOT" else ""
    dst_dir = os.path.join(NOTES_DIR, dest_folder.lstrip('/'))
    dst_file = os.path.join(dst_dir, os.path.basename(src))
    
    if os.path.exists(src):
        os.makedirs(dst_dir, exist_ok=True)
        shutil.move(src, dst_file)
    return jsonify({"status": "success"})

@app.route('/api/trash_list')
@login_required
def trash_list():
    return jsonify(os.listdir(TRASH_DIR))

@app.route('/trash_op', methods=['POST'])
@login_required
def trash_op():
    data = request.json
    action, name = data['action'], data['name']
    if action == 'to_trash':
        src = os.path.join(NOTES_DIR, name.lstrip('/'))
        dst = os.path.join(TRASH_DIR, datetime.now().strftime("%Y%m%d_%H%M_") + os.path.basename(name))
        if os.path.exists(src): 
            shutil.move(src, dst)
    elif action == 'restore':
        src = os.path.join(TRASH_DIR, name)
        orig = "_".join(name.split("_")[2:])
        dst = os.path.join(NOTES_DIR, orig)
        if os.path.exists(src): 
            shutil.move(src, dst)
    elif action == 'purge':
        p = os.path.join(TRASH_DIR, name)
        if os.path.exists(p):
            if os.path.isdir(p): 
                shutil.rmtree(p)
            else: 
                os.remove(p)
    return jsonify({"status": "success"})

if __name__ == '__main__':
    # Port is set to 5000, you can change it if needed. Remember this is not a production server, so don't expose it to the internet without proper security measures!
    # Make sure to consider all risks before doing so, and ideally use a reverse proxy with HTTPS and authentication in front of it.
    app.run(host='0.0.0.0', port=5000, debug=True)