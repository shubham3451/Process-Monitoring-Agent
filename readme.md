# Process Monitoring Agent

A full-stack **system monitoring solution** consisting of:

* **Agent** → Runs on the monitored host. Collects system metrics and sends them to backend.
* **Backend API** (Django REST + Channels) → Stores metrics, provides WebSocket & REST APIs.
* **Frontend Dashboard** → A modern web UI that displays host details, live processes, and historical processes.

---

##  Features

***Agent**: Collects CPU, memory, process details, sends to server.
***Live Processes**: Real-time updates over WebSocket.
***Historical Processes**: Paginated snapshots of past process states.
***Modern UI**: Responsive, card-based design with live + history views.

---

## Project Structure

```
system-monitoring/
│── agent/               # Python agent (can be bundled into exe)
│   └── agent.py
│
│── backend/             # Django backend
│   ├── manage.py
│   ├── monitoring/      # Django app
│   ├── settings.py
│   └── ...
│
│── frontend/            # Web frontend
│   ├── index.html
│   ├── css/styles.css
│   └── js/dashboard.js
│
└── README.md
```

---

## ⚙️ Backend Setup

### 1️. Clone repo & install dependencies

```bash
git clone https://github.com/yourusername/system-monitoring.git
cd system-monitoring/backend
python -m venv venv
source venv/bin/activate   # (Linux/Mac)
venv\Scripts\activate      # (Windows)

pip install -r requirements.txt
```

### 2️. Apply migrations & run backend

```bash
python manage.py makemigrations
python manage.py migrate
daphne backend.asgi:application -p 8000
```

Backend is now running at:

* REST API → `http://localhost:8000/api/`
* WebSocket → `ws://localhost:8000/ws/hosts/${HOSTNAME}/`

---

##  Frontend Setup

### 1️. Go to frontend folder

```bash
cd ../frontend
```

### 2️. Open in browser

Just open `index.html` in your browser.
*(If you need CORS handling, serve via `http-server` or Nginx)*



Dashboard will be available at → `http://localhost:3000` or `http://localhost:5500`

---

##  Agent Setup

The **agent** collects host details + processes and pushes to the backend.

### 1️. Install dependencies

```bash
cd ../agent
pip install -r requirements.txt
```

### 2️. Run agent

```bash
python agent.py 

### 3️. Bundle agent into `.exe` (Windows)

```bash
pip install pyinstaller
pyinstaller --onefile agent.py
```

This creates:

```
dist/agent.exe
```

Run with:

```bash
agent.exe
```

---

##  Configuration Changes (before running)

* **Backend URL** in `frontend/js/dashboard.js`

  ```js
  const API_BASE = "http://localhost:8000/api";
  const WS_URL   = `ws://localhost:8000/ws/hosts/${HOSTNAME}/`
  const HOSTNAME = "ubuntu";   // must match agent --host
  ```



##  Common Commands

### Backend

```bash
daphne backend.asgi:application -p 8000 or python manage.py runserver(if websocket support not nedded)
```

### Frontend

```bash
python3 -m http.server 3000
```


### Agent

```bash
python agent.py
```

### Build Agent EXE

```bash
pyinstaller --onefile agent.py
```

---

##  Workflow

1. Start **backend** (`python manage.py runserver`).
2. Run **agent** (`python agent.py or run agent.exe).
3. Open **frontend** (`index.html` / served locally).
4. Watch **live processes + history** update in real time.

---

