from django.shortcuts import render
from django.http import StreamingHttpResponse, JsonResponse
import cv2
import numpy as np
from keras.models import load_model
import os

# Define paths for model and labels
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, "asl_model.h5")
labels_path = os.path.join(BASE_DIR, "asl_labels.txt")

# Load the trained ASL model
model = load_model(model_path)

# Load labels from asl_labels.txt
with open(labels_path, "r") as f:
    labels = [line.strip() for line in f.readlines()]

# Initialize the video capture from webcam
camera = cv2.VideoCapture(0)


def predict_sign(frame):
    """
    Preprocess the frame and predict the sign using the trained model.
    """
    resized_frame = cv2.resize(frame, (64, 64))  # Resize frame to model input size
    img_array = np.expand_dims(resized_frame, axis=0) / 255.0  # Normalize to [0, 1]
    predictions = model.predict(img_array)  # Get predictions
    predicted_class = np.argmax(predictions[0])  # Get predicted class
    confidence = round(predictions[0][predicted_class] * 100, 2)
    return labels[predicted_class], confidence


def generate_frames():
    """
    Capture and generate frames for the video feed.
    """
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Predict sign and display results on frame
            sign, confidence = predict_sign(frame)
            cv2.putText(frame, f"{sign} ({confidence}%)", (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

            # Encode the frame as JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()

            # Yield the frame for streaming
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


def index(request):
    """
    Render the main page with the video feed.
    """
    return render(request, 'sign_language/index.html')

def sign_language_recognition(request):
    # Your logic here
    return render(request, 'sign_language/sign_language_recognition.html')

def video_feed(request):
    """
    Provide video feed to the browser.
    """
    return StreamingHttpResponse(generate_frames(), content_type='multipart/x-mixed-replace; boundary=frame')


def predict(request):
    """
    Predict sign from the current frame and return the result.
    """
    success, frame = camera.read()
    if success:
        sign, confidence = predict_sign(frame)
        return JsonResponse({"sign": sign, "confidence": confidence})
    return JsonResponse({"error": "No frame available"})
