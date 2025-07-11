from django.http import StreamingHttpResponse, JsonResponse
from django.shortcuts import render
import cv2
import numpy as np
import os
import mediapipe as mp
from tensorflow.keras.models import load_model

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, "mediapipe_model.h5")
model = load_model(model_path)

# MediaPipe hands setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Store the last detected sign for "Detect Sign" button
last_detected_sign = {"sign": "None", "confidence": 0.0}

# ----- 1. Generate Frames with Real-time Sign Detection -----
def generate_frames():
    """Generates frames with real-time sign detection."""
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

#frame skipping for performance
    frame_count = 0
    process_every_n_frames = 2  # Process every 2nd frame

    while True:
        success, frame = cap.read()
        if not success:
            print("Failed to capture webcam feed.")
            break
        
        # Flip the frame horizontally for a mirror effect
        frame = cv2.flip(frame, 1)

        # Convert frame to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        predicted_sign, confidence = "None", 0.0

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Extract landmarks for prediction
                landmarks = []
                for lm in hand_landmarks.landmark:
                    landmarks.extend([lm.x, lm.y, lm.z])  # Extracts 3D coordinates 

                # Prepare landmarks for model input
                landmarks = np.array(landmarks).reshape(1, -1)

                # Predict the sign
                prediction = model.predict(landmarks)
                predicted_label = np.argmax(prediction)
                confidence = round(float(np.max(prediction)) * 100, 2)

                # Define label based on predicted label index
                sign_labels = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "none"]  
                predicted_sign = sign_labels[predicted_label]

                # Update last detected sign
                global last_detected_sign
                last_detected_sign["sign"] = predicted_sign
                last_detected_sign["confidence"] = confidence

        # Display prediction in top-left corner
        cv2.putText(frame, f"{predicted_sign} ({confidence}%)", (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        # Encode frame as JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        # Yield frame for streaming
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


def video_feed(request):
    """Handles video streaming at /video_feed/."""
    return StreamingHttpResponse(generate_frames(), content_type='multipart/x-mixed-replace; boundary=frame')


# ----- 2. Detect Sign on Button Click -----
def detect_sign(request):
    """Detect the sign when the button is clicked and return the result."""
    global last_detected_sign
    
    # Ensure we're not returning "none" as a sign
    sign = last_detected_sign["sign"]
    confidence = last_detected_sign["confidence"]
    
    # Debug logging
    print(f"Detected sign: {sign} with confidence {confidence}")
    
    # Only return valid signs (not "none" or "None")
    if sign.lower() == "none":
        sign_data = {
            "sign": "None",
            "confidence": 0.0
        }
    else:
        sign_data = {
            "sign": sign,
            "confidence": float(confidence)
        }
    
    return JsonResponse({"result": sign_data})

# ----- 3. Render Main Page -----
def index(request):
    """Render the main sign language recognition page."""
    return render(request, 'sign_language/sign_language.html')
