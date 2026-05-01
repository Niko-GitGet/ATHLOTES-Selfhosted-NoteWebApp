import os
import shutil
import json
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'athl_v54_ultra_single'

# ── Storage Paths ─────────────────────────────────────────────────────────────
BASE_DIR = os.getcwd()
DATA_DIR = '/app/data' if os.path.exists('/app/data') else os.path.join(BASE_DIR, 'data')
CONFIG_FILE = os.path.join(DATA_DIR, 'config.json')
NOTES_DIR  = os.path.join(DATA_DIR, 'notes')
TRASH_DIR  = os.path.join(DATA_DIR, 'trash')

for d in [DATA_DIR, NOTES_DIR, TRASH_DIR]:
    os.makedirs(d, exist_ok=True)

# ── Single hard-coded credential (change here to update login) ────────────────
USERNAME = "your_username_here"
PIN      = "your_pin_here"

# ── Auth ──────────────────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/login')
def login():
    if 'username' in session:
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    if data.get('user', '').strip() == USERNAME and data.get('pin', '') == PIN:
        session['username'] = USERNAME
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "denied"}), 401

@app.route('/api/users', methods=['GET'])
def api_get_users():
    return jsonify([USERNAME])

# ── Habit Tracker ─────────────────────────────────────────────────────────────
HABITS_FILE = os.path.join(DATA_DIR, 'habits.json')

@app.route('/api/habits', methods=['GET'])
@login_required
def get_habits():
    if os.path.exists(HABITS_FILE):
        with open(HABITS_FILE, 'r') as f:
            return jsonify(json.load(f))
    return jsonify({})

@app.route('/api/habits', methods=['POST'])
@login_required
def save_habits():
    with open(HABITS_FILE, 'w') as f:
        json.dump(request.json, f, indent=2)
    return jsonify({"status": "success"})

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# ── Config (Theme + Background) ───────────────────────────────────────────────
@app.route('/api/config', methods=['GET'])
@login_required
def get_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return jsonify(json.load(f))
    return jsonify({})

@app.route('/api/config', methods=['POST'])
@login_required
def save_config():
    with open(CONFIG_FILE, 'w') as f:
        json.dump(request.json, f, indent=2)
    return jsonify({"status": "success"})

# ── Main App ──────────────────────────────────────────────────────────────────
@app.route('/')
@login_required
def index():
    return render_template('index.html', username=USERNAME)

# ── File Tree ─────────────────────────────────────────────────────────────────
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
            except PermissionError:
                pass
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
        if not os.path.exists(full_path):
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
            shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    return jsonify({"status": "success"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
