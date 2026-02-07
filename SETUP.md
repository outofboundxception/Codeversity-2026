# ISL Translator Setup Guide

## Prerequisites
- Python 3.11+
- Node.js 18+
- Webcam

## Backend Setup

### Mac/Linux:
```bash
cd isl-backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Windows:
```powershell
cd isl-backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app:app --reload --port 8000
```

**Verify backend is running:**
Open browser: http://localhost:8000
Should see: `{"status":"running","service":"ISL Translator API","version":"1.0.0"}`

## Frontend Setup

```bash
cd igu
npm install
npm run dev
```

Open browser: http://localhost:5173

## Testing

1. Start backend first (port 8000)
2. Start frontend (port 5173)
3. Click "✋ Gesture → 🔊 Speech"
4. Allow camera access
5. Click "▶ Start Recording"
6. Show your hand to the camera
7. You should see gesture predictions!

## Troubleshooting

### Backend Issues

**NumPy Error:**
```bash
pip uninstall numpy
pip install "numpy<2.0"
```

**Port 8000 already in use:**
```bash
# Mac/Linux
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER>
```
