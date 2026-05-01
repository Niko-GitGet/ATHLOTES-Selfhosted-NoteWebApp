# ATHLOTES — Setup Guide

A self-hosted notes, habits, and task management app built with Flask.

---

## Project Structure

```
athlotes/
├── app.py                  # Flask backend
├── requirements.txt        # Python dependencies
├── templates/
│   ├── index.html          # Main app UI
│   └── login.html          # Login page
├── static/
│   └── background1.webp    # Background image
└── data/                   # Auto-created at runtime
    ├── config.json
    ├── habits.json
    ├── notes/
    └── trash/
```

---

## Background Images

ATHLOTES expects up to **5 background images** in the `static/` folder. These are not included in the repository — you need to provide your own.

The files must be named exactly as follows:

```
static/
├── background1.webp
├── background2.webp
├── background3.webp
├── background4.webp
└── background5.webp
```

The app defaults to `background1.webp` on first load. The in-app settings panel lets you switch between all five. Only `background1.webp` is strictly required for the app to display correctly — the others are optional slots you can fill as you like.

**Format:** `.webp` is required (the filenames are hardcoded). You can convert any photo to webp using tools like [Squoosh](https://squoosh.app) (free, browser-based) or ImageMagick:

```bash
magick input.jpg -quality 85 background1.webp
```

**Recommended specs:** full-screen landscape photos work best. Aim for around 1920×1080 or higher, and keep file sizes reasonable (under 1 MB per image) since they load on every page visit. The app applies a heavy blur and dark overlay on top, so high-frequency detail matters less than overall composition and color.

> The `static/` folder should exist in your repo (add a `.gitkeep` file inside it to track the empty folder). Add the actual `.webp` files to `.gitignore` if you prefer not to commit large images to the repo.

---

## 1. Run Locally (Python)

### Prerequisites
- Python 3.9+
- pip

### Steps

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/athlotes.git
cd athlotes

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py
```

The app will be available at **http://localhost:5000**

### Credentials

The credentials are set directly in `app.py`. Open the file and look for these two lines near the top:

```python
USERNAME = "your_username_here"
PIN      = "your_pin_here"
```

Replace the placeholder values with whatever User ID and PIN you want to use, then save the file before running the app.

> ⚠️ **Keep the repo private.** Since credentials are stored as plain text in `app.py`, a public repository would expose them to anyone. Go to your GitHub repo → **Settings** → **Danger Zone** → **Change visibility** → **Private**.

### requirements.txt

If you don't have one yet, create it with:

```
flask>=3.0.0
```

---

## 2. Run Locally via Docker

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)

### Dockerfile

Create a `Dockerfile` in the project root:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data/notes /app/data/trash

EXPOSE 5000

CMD ["python", "app.py"]
```

### Build & Run

```bash
# Build the image
docker build -t athlotes .

# Run with a persistent data volume
docker run -d \
  -p 5000:5000 \
  -v athlotes_data:/app/data \
  --name athlotes \
  athlotes
```

App is available at **http://localhost:5000**

### Useful Docker Commands

```bash
docker logs athlotes        # View logs
docker stop athlotes        # Stop the container
docker start athlotes       # Restart it
docker rm athlotes          # Remove the container
```

---

## 3. Self-Host on a Local Server (LAN)

Run ATHLOTES on a machine in your home network so any device on the same Wi-Fi can access it.

### Steps

1. Follow the **Local (Python)** steps above on your server machine.
2. Find the server's local IP address:

```bash
# macOS/Linux
ip a | grep "inet "

# Windows
ipconfig
```

3. The app already binds to `0.0.0.0` (all interfaces), so it will be reachable at:

```
http://<SERVER_LAN_IP>:5000
```

### Run as a Background Service (Linux — systemd)

```ini
# /etc/systemd/system/athlotes.service

[Unit]
Description=ATHLOTES App
After=network.target

[Service]
WorkingDirectory=/home/YOUR_USER/athlotes
ExecStart=/home/YOUR_USER/athlotes/venv/bin/python app.py
Restart=always
User=YOUR_USER
Environment=PORT=5000

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable athlotes
sudo systemctl start athlotes
```

---

## 4. Deploy to the Cloud (Railway as an Example)

There are many platforms that can host a Flask app — **Railway, Render, Fly.io, a VPS (Hetzner, DigitalOcean), etc.** The steps below use Railway as a concrete example, but the general approach is the same everywhere: give the platform your code, set environment variables for secrets, and attach persistent storage so your data survives redeploys.

> ⚠️ **Public web app warning — read before deploying.**
> Once deployed to the cloud, your ATHLOTES instance is reachable by anyone on the internet. The app has only a single username/PIN for protection and no rate limiting or brute-force lockout. Before going live you **must**:
> - Set a strong, unique PIN (not a short number)
> - Change the `SECRET_KEY` to a long random string (see Security Notes below)
> - Keep the GitHub repo **private** so credentials are never exposed
> - Use HTTPS (Railway provides this automatically; other platforms vary)
>
> If you just need personal access, the LAN server setup (Section 3) is safer and simpler.

### Prerequisites
- A GitHub account with the repo pushed as a **private** repository
- A [Railway](https://railway.app) account (free tier works)

### Steps

**1. Add a `Procfile`** to the project root:

```
web: python app.py
```

**2. Set the PORT via environment variable**

The app already reads `PORT` from the environment:
```python
port = int(os.environ.get("PORT", 5000))
```
Railway injects this automatically — no changes needed.

**3. Push to GitHub**

```bash
git add .
git commit -m "ready for Railway"
git push origin main
```

**4. Create a Railway project**

- Go to [railway.app](https://railway.app) → **New Project**
- Select **Deploy from GitHub repo**
- Choose your `athlotes` repository
- Railway auto-detects Python and deploys

**5. Add a persistent volume — this step is required**

Without a volume, every redeploy wipes your notes, habits, and config. Railway containers have no persistent disk by default.

- In your Railway project dashboard, click your service
- Go to the **Volumes** tab → **Add Volume**
- Set the **Mount Path** to `/app/data`
- Click **Create** — Railway will restart the service with the volume attached

From this point on, everything written to `/app/data` (notes, habits, config) survives redeploys and restarts.

**6. Get your public URL**

- Railway tab → **Settings** → **Domains** → **Generate Domain**
- Your app is now live at `https://athlotes-xxxx.up.railway.app`

### Environment Variables on Railway

Set these in **Railway → your service → Variables**:

| Variable | Purpose |
|----------|---------|
| `SECRET_KEY` | A long random string — **required** before going public (see Security Notes) |
| `PORT` | Injected automatically by Railway, do not set manually |

---

## Security Notes

### Credentials

The `USERNAME` and `PIN` are plain text constants in `app.py`. Anyone who can read the file can log in, so keep the repo private and choose a PIN that isn't trivially guessable.

### The Secret Key — what it is and why it matters

Near the top of `app.py` you'll find:

```python
app.secret_key = 'athl_v54_ultra_single'
```

Flask uses this string to **cryptographically sign session cookies**. When you log in, Flask creates a cookie in your browser that says "this user is authenticated." That cookie is signed with the secret key — if someone doesn't know the key they can't forge a valid cookie and bypass the login.

If the secret key is:
- **Short or guessable** — an attacker could brute-force it and forge session cookies, gaining access without a password
- **Hardcoded and in a public repo** — anyone can read it from GitHub and do the same

**Before deploying publicly, replace it** with a long random string loaded from an environment variable:

```python
# In app.py — replace the hardcoded line with:
app.secret_key = os.environ.get("SECRET_KEY", "only-used-locally")
```

Then set `SECRET_KEY` in your hosting platform's environment variables (e.g. Railway → your service → Variables). Generate a strong value with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### HTTPS

Railway provides HTTPS automatically on generated domains. For self-hosted LAN setups, HTTPS is optional since traffic stays on your local network. If you expose the app to the internet on your own server, put it behind a reverse proxy like Nginx with a free Certbot/Let's Encrypt certificate.

---

## Quick Reference

| Setup | URL | Best For |
|-------|-----|---------|
| Local Python | `localhost:5000` | Development |
| Local Docker | `localhost:5000` | Clean isolated dev |
| LAN Server | `192.168.x.x:5000` | Home network access |
| Railway | `https://your-app.up.railway.app` | Public cloud access |
