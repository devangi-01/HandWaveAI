import cv2
import numpy as np
from tensorflow.keras.models import load_model

# Load class labels dynamically from asl_labels.txt
label_path = 'sign_language/asl_labels.txt'
with open(label_path, 'r') as f:
    class_labels = [line.strip() for line in f.readlines()]

# Load the trained ASL model (RGB input, 100x100)
model_path = 'sign_language/asl_model.h5'
model = load_model(model_path)

def detect_asl(frame):
    """Detect ASL sign from a given frame"""
    # Resize the frame to 100x100 to match the model input
    frame_resized = cv2.resize(frame, (100, 100))  # Resize to 100x100
    frame_normalized = frame_resized / 255.0  # Normalize pixel values to [0, 1]

    # Expand dimensions to match the input shape of the model
    frame_input = np.expand_dims(frame_normalized, axis=0)  # Shape: (1, 100, 100, 3)

    # Get model predictions
    predictions = model.predict(frame_input)

    # Get the index of the highest probability
    predicted_class_index = np.argmax(predictions[0])
    confidence = predictions[0][predicted_class_index]

    # Return the detected sign if confidence is above the threshold
    if confidence > 0.8:  # Confidence threshold can be adjusted
        return class_labels[predicted_class_index]
    else:
        return None
