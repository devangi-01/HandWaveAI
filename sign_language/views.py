from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse

def sign_language_recognition(request):
    return JsonResponse({'message': 'Sign Language Recognition Coming Soon!'})


# from django.http import StreamingHttpResponse
# from django.shortcuts import render
# import cv2
# import numpy as np
# import pyttsx3
# from keras.models import load_model

# # Load the pretrained CNN model
# MODEL_PATH = "model.h5"
# model = load_model(MODEL_PATH)

# # Labels for ASL letters
# LABELS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 
#           'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

# THRESHOLD = 25  # Minimum confidence for valid prediction
# IMAGE_SIZE = 50  # CNN model input size

# # Initialize text-to-speech engine
# engine = pyttsx3.init()
# engine.setProperty('rate', 110)

# def pre_process(img_array):
#     """ Convert image to grayscale, resize, normalize, and reshape for model. """
#     img_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
#     img_array = cv2.resize(img_array, (IMAGE_SIZE, IMAGE_SIZE))
#     img_array = img_array.reshape(IMAGE_SIZE, IMAGE_SIZE, 1)  # Reshape for CNN
#     img_array = img_array / 255.0  # Normalize
#     img_array = np.expand_dims(img_array, axis=0)  # Expand dimensions for model input
#     return img_array

# def predict_sign(img_array):
#     """ Predicts the letter from the preprocessed hand gesture image. """
#     img_array = pre_process(img_array)
#     preds = model.predict(img_array)
#     preds *= 100  # Convert probability to percentage
#     most_likely_class_index = int(np.argmax(preds))
#     return preds.max(), LABELS[most_likely_class_index]

# def generate_frames():
#     """ Captures webcam frames and processes hand gestures for ASL recognition. """
#     cap = cv2.VideoCapture(0)
#     sentence = ""
#     x_start, y_start, roi_width, roi_height = 100, 100, 200, 200

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break

#         # Draw bounding box for hand tracking
#         cv2.rectangle(frame, (x_start, y_start), (x_start + roi_width, y_start + roi_height), (255, 0, 0), 3)
        
#         # Crop ROI (Region of Interest)
#         roi = frame[y_start:y_start + roi_height, x_start:x_start + roi_width]

#         # Convert to YCrCb for better skin detection
#         img_ycrcb = cv2.cvtColor(roi, cv2.COLOR_BGR2YCR_CB)
#         blur = cv2.GaussianBlur(img_ycrcb, (11, 11), 0)

#         # Define skin color range in YCrCb
#         skin_ycrcb_min = np.array((0, 138, 67), dtype=np.uint8)
#         skin_ycrcb_max = np.array((255, 173, 133), dtype=np.uint8)

#         # Create mask for skin detection
#         mask = cv2.inRange(blur, skin_ycrcb_min, skin_ycrcb_max)
#         kernel = np.ones((2, 2), dtype=np.uint8)
#         mask = cv2.dilate(mask, kernel, iterations=1)

#         # Bitwise mask for hand extraction
#         hand_segment = cv2.bitwise_and(roi, roi, mask=mask)

#         # Predict sign if hand is detected
#         if hand_segment.shape[0] > 0 and hand_segment.shape[1] > 0:
#             conf, label = predict_sign(hand_segment)
#             if conf >= THRESHOLD:
#                 cv2.putText(frame, label, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
#         # Encode frame to JPEG format
#         _, buffer = cv2.imencode('.jpg', frame)
#         frame_bytes = buffer.tobytes()

#         # Yield frame bytes for streaming
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

#     cap.release()
#     cv2.destroyAllWindows()

# def stream_video(request):
#     """ Django view to stream real-time ASL recognition. """
#     return StreamingHttpResponse(generate_frames(), content_type="multipart/x-mixed-replace; boundary=frame")

# def index(request):
#     """ Renders the HTML template for ASL recognition. """
#     return render(request, 'asl_recognition.html')
