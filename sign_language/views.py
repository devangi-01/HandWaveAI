# from django.shortcuts import render
# from django.http import StreamingHttpResponse, JsonResponse
# import cv2
# import numpy as np
# from keras.models import load_model
# import os

# # Define paths for model and labels
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# model_path = os.path.join(BASE_DIR, "asl_model.h5")
# labels_path = os.path.join(BASE_DIR, "asl_labels.txt")

# # Load the trained ASL model
# model = load_model(model_path)

# # Load labels from asl_labels.txt
# with open(labels_path, "r") as f:
#     labels = [line.strip() for line in f.readlines()]

# # Initialize the video capture from webcam
# camera = cv2.VideoCapture(0)


# def predict_sign(frame):
#     """
#     Preprocess the frame and predict the sign using the trained model.
#     """
#     resized_frame = cv2.resize(frame, (100, 100))  # Resize frame to model input size
#     img_array = np.expand_dims(resized_frame, axis=0) / 255.0  # Normalize to [0, 1]
#     predictions = model.predict(img_array)  # Get predictions
#     predicted_class = np.argmax(predictions[0])  # Get predicted class
#     confidence = round(predictions[0][predicted_class] * 100, 2)
#     return labels[predicted_class], confidence


# def generate_frames():
#     """
#     Capture and generate frames for the video feed.
#     """
#     while True:
#         success, frame = camera.read()
#         if not success:
#             break
#         else:
#             # Predict sign and display results on frame
#             sign, confidence = predict_sign(frame)
#             cv2.putText(frame, f"{sign} ({confidence}%)", (10, 50),
#                         cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

#             # Encode the frame as JPEG
#             _, buffer = cv2.imencode('.jpg', frame)
#             frame_bytes = buffer.tobytes()

#             # Yield the frame for streaming
#             yield (b'--frame\r\n'
#                    b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


# def index(request):
#     """
#     Render the HandWave AI main page.
#     """
#     return render(request, 'index.html')


# def sign_language_recognition(request):
#     """
#     Render the advanced sign language recognition page.
#     """
#     return render(request, 'sign_language/sign_language_recognition.html')


# def sign(request):
#     """
#     Render the simple sign language recognition page.
#     """
#     return render(request, 'sign_language/sign_language.html')


# def video_feed(request):
#     """
#     Provide video feed to the browser.
#     """
#     return StreamingHttpResponse(generate_frames(), content_type='multipart/x-mixed-replace; boundary=frame')


# def predict(request):
#     """
#     Predict sign from the current frame and return the result.
#     """
#     success, frame = camera.read()
#     if success:
#         sign, confidence = predict_sign(frame)
#         return JsonResponse({"sign": sign, "confidence": confidence})
#     return JsonResponse({"error": "No frame available"})
from django.http import StreamingHttpResponse, JsonResponse
from django.shortcuts import render
import cv2
import numpy as np
import mediapipe as mp
import os
from tensorflow.keras.models import load_model

# Load trained MediaPipe + AI model
model_path = r"P:\handwave_ai\sign_language\mediapipe_model.h5"
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
    

    while True:
        success, frame = cap.read()
        if not success:
            print("Failed to capture webcam feed.")
            break
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
                    landmarks.extend([lm.x, lm.y, lm.z])

                # Prepare landmarks for model input
                landmarks = np.array(landmarks).reshape(1, -1)

                # Predict the sign
                prediction = model.predict(landmarks)
                predicted_label = np.argmax(prediction)
                confidence = round(np.max(prediction) * 100, 2)

                # Define label based on predicted label index
                sign_labels = ["A", "B", "C", "D", "E", "F"]  # Update as per your labels
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
    sign_data = {
        "sign": last_detected_sign["sign"],
        "confidence": last_detected_sign["confidence"]
    }
    return JsonResponse({"result": sign_data})


# ----- 3. Render Main Page -----
def index(request):
    """Render the main sign language recognition page."""
    return render(request, 'sign_language/sign_language.html')
