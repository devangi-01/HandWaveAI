import os
import cv2
import numpy as np
import mediapipe as mp
# from tensorflow.keras.models import load_model
from tensorflow.python.keras.models import load_model


from django.conf import settings

# Load ASL Model
model_path = os.path.join(settings.BASE_DIR, "sign_language/model.h5")
model = load_model(model_path)

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

def detect_asl(frame):
    """Processes a frame and returns the detected ASL letter"""
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Extract hand bounding box
            x_min, y_min, x_max, y_max = 9999, 9999, 0, 0
            for lm in hand_landmarks.landmark:
                x, y = int(lm.x * frame.shape[1]), int(lm.y * frame.shape[0])
                x_min, y_min = min(x, x_min), min(y, y_min)
                x_max, y_max = max(x, x_max), max(y, y_max)

            # Crop and preprocess hand region
            hand_crop = frame[y_min:y_max, x_min:x_max]
            hand_crop = cv2.resize(hand_crop, (64, 64))
            hand_crop = cv2.cvtColor(hand_crop, cv2.COLOR_BGR2GRAY)
            hand_crop = hand_crop / 255.0
            hand_crop = np.expand_dims(hand_crop, axis=[0, -1])

            # Predict ASL sign
            prediction = model.predict(hand_crop)
            label = np.argmax(prediction)  # Convert to class label

            return str(label)  # Return detected sign

    return None
