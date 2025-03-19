import cv2
import numpy as np
from tensorflow.keras.models import load_model

# Load class labels from asl_labels.txt
label_path = 'sign_language/asl_labels.txt'
with open(label_path, 'r') as f:
    class_labels = [line.strip() for line in f.readlines()]

# Load the trained ASL model
model_path = 'sign_language/asl_model.h5'
model = load_model(model_path)

def detect_asl(frame):
    """Detect ASL sign from a given frame"""
    # Preprocess the frame to match the input shape of the model
    frame_resized = cv2.resize(frame, (64, 64))  # Resize to 64x64
    frame_gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
    frame_normalized = frame_gray / 255.0  # Normalize pixel values to [0, 1]

    # Expand dimensions to match model input shape
    frame_input = np.expand_dims(frame_normalized, axis=0).reshape(-1, 64, 64, 1)

    # Get model predictions
    predictions = model.predict(frame_input)

    # Get the index of the highest probability
    predicted_class_index = np.argmax(predictions[0])
    confidence = predictions[0][predicted_class_index]

    # Return detected class if confidence is high enough
    if confidence > 0.8:  # Adjust the threshold if necessary
        return class_labels[predicted_class_index]
    else:
        return None
