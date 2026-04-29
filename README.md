# ATHLOTES Alpha V.54 Release.1

ATHLOTES is a high-performance, glassmorphic web-based note-taking application designed for speed and aesthetic clarity. The workspace features a dual-pane split view for seamless multitasking, a custom theme engine, and a robust recovery hub for deleted entries.

## 📂 Project Structure

To ensure the application runs correctly, organize your files in the following hierarchy:

*   **app.py** (Main Flask Backend)
*   **static/** (Folder for assets)
    *   background1.png
*   **templates/** (Folder for UI files)
    *   index.html
    *   login.html
*   **notes/** (Automatically created storage)
*   **trash/** (Automatically created recovery hub)

## 🛠️ Installation (Ubuntu Server)

### 1. File Setup
Transfer your project files to the server via SSH or create them directly on the machine. Simply **copy the content** of your local `app.py`, `index.html`, and `login.html` into the respective files on your server.

### 2. Configuration & Credentials
To secure your application, you must set your own access data. You can find the credentials at the top of the **app.py** file. Look for the following lines and **edit them** before starting the app:
*   `AUTH_USER = "YourUsername"`
*   `AUTH_PIN = "YourSecretPin"`

### 3. Setup Environment
Update your system and install the required Python components:
`sudo apt update && sudo apt upgrade -y`
`sudo apt install python3-pip python3-venv -y`

Navigate to your directory, create a virtual environment, and install Flask:
`python3 -m venv venv`
`source venv/bin/activate`
`pip install flask`

### 4. Run the App
Launch the server on the default port 5000 by executing:
`python3 app.py`

## 🔒 Security Reminder

> [!WARNING]
> This application is intended for private use. If you plan to access ATHLOTES outside of your local network, ensure you implement a secure hosting environment and enable HTTPS/SSL to protect your login data and personal notes.
