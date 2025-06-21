# 🤚 HandWave AI

HandWave AI is an innovative web-based platform that uses real-time hand gesture recognition powered by machine learning and computer vision. It includes three main interactive applications:

- ✏️ **Math Solver** – Solve handwritten math problems using gestures
- 🧏 **Sign Language Recognition** – Translate ASL into text
- 🧠 **Gesture Quiz** – Answer quiz questions using finger gestures

---

## 📸 Live Demo

> Coming soon or deploy locally using the guide below.

---

## 🧑‍💻 Features

### 📐 Math Solver
- Draw equations using your index finger
- Thumbs-up gesture to solve with AI
- Upload math images for analysis
- AI-powered by Gemini (Google)

### 🤟 Sign Language Recognition
- Detect A–Z ASL gestures
- Real-time prediction with confidence scores
- Sign history to build full sentences

### ✋ Gesture Quiz
- Answer MCQs with 1–4 fingers
- Score tracking and gesture-based input

---

## 🚀 Getting Started

### ✅ Requirements
- Python 3.8+
- pip
- Git
- Webcam
- Internet Connection

### 🔧 Installation

#### Dependencies require

django==4.2.0
opencv-python==4.7.0.72
numpy==1.24.3
mediapipe==0.10.0
cvzone==1.5.6
tensorflow==2.12.0
google-generativeai==0.3.0
pandas==2.0.1
playsound==1.3.0
pillow==9.5.0


```bash
# Clone the repository
git clone https://github.com/devangi-01/HandWaveAI.git
cd handwave-ai

# Create and activate virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Add your Google Gemini API key
echo GEMINI_API_KEY=your_key_here > .env

# Run migrations and start the server
python manage.py migrate
python manage.py runserver

