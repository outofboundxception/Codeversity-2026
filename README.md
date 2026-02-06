# ISL Connect

ISL Connect is a web-based AI application designed to enable real-time, two-way communication between Indian Sign Language (ISL) users and the general population. The system bridges the communication gap by translating ISL hand gestures into text and speech, and converting spoken or textual input into sign language representations.

The project focuses on accessibility, inclusivity, and affordability by using open-source tools and standard hardware such as webcams, making it suitable for real-world deployment on low-cost devices.

---

## Problem Statement

Communication between hearing- and speech-impaired individuals and non-signers remains a major challenge due to limited awareness and adoption of Indian Sign Language. This issue is especially prominent in education, healthcare, and public service environments.

ISL Connect aims to address this gap by providing a real-time, AI-powered translation system that enables seamless interaction between ISL users and non-sign language users.

---

## Features

- Real-time Indian Sign Language gesture recognition using a webcam
- Translation of ISL gestures into readable text
- Text-to-speech conversion for audible output
- Speech or text input converted into ISL gesture representations
- Web-based interface with no special hardware requirements
- Built entirely using open-source technologies
- Optimized for low-cost and resource-constrained devices

---

## Tech Stack

### Frontend
- React (18.x)
- Vite (5.x)
- JavaScript (ES6+)
- Axios
- HTML5 Canvas API
- MediaDevices API
- Web Speech API
- CSS3

### Backend
- Python (3.11)
- FastAPI
- Uvicorn
- Pydantic
- MediaPipe
- OpenCV
- NumPy
- Pillow

---

## System Architecture

1. The user’s webcam captures live video input.
2. Video frames are processed in real time using OpenCV and MediaPipe.
3. Hand landmarks are extracted and analyzed for gesture recognition.
4. Recognized gestures are translated into text and speech.
5. User speech or text input is processed and converted into ISL representations.
6. The frontend displays the output in an interactive and user-friendly format.

---

## Installation and Setup

### Prerequisites
- Node.js (v18 or above recommended)
- Python 3.11
- Webcam-enabled device

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
---

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```
