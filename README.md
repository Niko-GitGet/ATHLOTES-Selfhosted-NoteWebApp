# ATHLOTES — Self-Hosting & Deployment Guide

This guide covers two ways to run ATHLOTES: locally on your own machine, and in the cloud via Railway (recommended for always-on access from any device).

---

## Required Files

Before you start, make sure you have these files:

```
athlotes/
├── app.py
├── templates/
│   ├── index.html
│   └── login.html
├── static/
│   ├── background1.webp
│   ├── background2.webp
│   ├── background3.webp
│   ├── background4.webp
│   └── background5.webp
└── requirements.txt
```

Create `requirements.txt` with the following content:

```
flask>=3.0.0
gunicorn>=21.0.0
```

---

## Option A — Self-Hosting (Local Machine)

### 1. Install Python

Make sure Python 3.10 or newer is installed. Check with:

```bash
python3 --version
```

Download from [python.org](https://python.org) if needed.

### 2. Set Up the Project

```bash
# Clone or copy your project files into a folder
cd athlotes

# Create a virtual environment
python3 -m venv venv

# Activate it
# macOS / Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the App

```bash
python app.py
```

The app will be available at `http://localhost:5000`.

Your data is saved automatically in a `data/` folder next to `app.py`:

```
data/
├── notes/        ← all your note files
├── trash/        ← deleted items (recoverable)
├── habits.json   ← habit tracker data
└── config.json   ← theme & background settings
```

### 4. Change Login Credentials

Open `app.py` and find these two lines near the top:

```python
USERNAME = "Athl"
PIN      = "192.168"
```

Change them to whatever you want, then restart the app.

Also change the secret key to something unique and random:

```python
app.secret_key = 'your-long-random-string-here'
```

### 5. Run on Startup (optional)

**macOS / Linux** — create a simple shell script `start.sh`:

```bash
#!/bin/bash
cd /path/to/athlotes
source venv/bin/activate
python app.py
```

Make it executable: `chmod +x start.sh`

**Windows** — create `start.bat`:

```bat
cd C:\path\to\athlotes
venv\Scripts\activate
python app.py
```

---

## Option B — Railway (Cloud Hosting)

Railway runs your app 24/7 in the cloud, accessible from any device. A volume is required so your notes, habits, and settings survive redeploys.

### Step 1 — Create a GitHub Repository

1. Go to [github.com](https://github.com) and sign in (create a free account if needed).
2. Click **New repository** (the `+` button top-right → New repository).
3. Give it a name like `athlotes`, set it to **Private**, and click **Create repository**.
4. On your machine, open a terminal in your project folder and run:

```bash
git init
git add .
git commit -m "initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/athlotes.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username. Your code is now on GitHub.

> **Note:** Make sure `.gitignore` excludes the `data/` folder and `venv/` so personal data and the virtual environment are not pushed:
>
> ```
> data/
> venv/
> __pycache__/
> *.pyc
> ```

### Step 2 — Create a Railway Account

Go to [railway.app](https://railway.app) and sign up with your GitHub account. This lets Railway access your repositories directly.

### Step 3 — Create a New Project

1. In the Railway dashboard, click **New Project**.
2. Select **Deploy from GitHub repo**.
3. Find and select your `athlotes` repository.
4. Railway will detect it's a Python app and begin the first deployment.

### Step 4 — Add a Persistent Volume

Without a volume, all your notes and data will be wiped every time Railway redeploys your app. The volume makes `/app/data` permanent.

1. In your Railway project, click on your service (the athlotes box).
2. Go to the **Volumes** tab.
3. Click **Add Volume**.
4. Set the **Mount Path** to exactly:
   ```
   /app/data
   ```
5. Choose a size (1 GB is more than enough for notes).
6. Click **Create**.

Railway will redeploy automatically. From now on everything in `/app/data` — your notes, habits, config, and trash — persists permanently across all future deploys.

### Step 5 — Set Environment Variables

1. In your service, go to the **Variables** tab.
2. Add the following variable:

| Variable | Value |
|---|---|
| `SECRET_KEY` | a long random string, e.g. `xK9#mP2$qL7nR4` |

Then update `app.py` to read it:

```python
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-dev-key')
```

Push the change to GitHub — Railway will redeploy automatically.

### Step 6 — Get Your Public URL

1. Go to the **Settings** tab of your service.
2. Under **Networking**, click **Generate Domain**.
3. Railway gives you a public URL like `https://athlotes-production.up.railway.app`.

Open it in any browser, log in, and your app is live.

### Step 7 — Push Updates

Whenever you change your code:

```bash
git add .
git commit -m "describe your change"
git push
```

Railway detects the push and redeploys automatically. Your data on the volume is untouched.

---

## Credentials Reference

Default login (change these before going live):

| Field | Default value |
|---|---|
| Username | `Athl` |
| PIN | `192.168` |

To change them, edit these lines in `app.py`:

```python
USERNAME = "YourName"
PIN      = "YourPIN"
```

---

## Troubleshooting

**App won't start locally**
Make sure the virtual environment is activated (`source venv/bin/activate`) and dependencies are installed (`pip install -r requirements.txt`).

**Railway build fails**
Check that `requirements.txt` is present in the root of the repo and contains `flask` and `gunicorn`.

**Notes disappear after Railway redeploy**
The volume mount path must be exactly `/app/data`. Double-check there are no typos and that the volume is attached to the correct service.

**Can't reach the Railway URL**
Go to Settings → Networking and confirm a domain has been generated. If the deploy failed, check the build logs under the **Deployments** tab.

**Login not working**
Confirm `USERNAME` and `PIN` in `app.py` match exactly what you're typing. The username comparison is case-sensitive.
