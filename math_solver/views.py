# import os
# import cv2
# import numpy as np
# import time
# from django.shortcuts import render
# from django.http import StreamingHttpResponse, JsonResponse
# from cvzone.HandTrackingModule import HandDetector
# import google.generativeai as genai
# from PIL import Image

# # Load API Key securely
# genai.configure(api_key="AIzaSyCW6K9DW9rvuoMJpZAdlBuRMjH6Qg13P7U")
# model = genai.GenerativeModel("gemini-1.5-flash")

# # Initialize Hand Detector
# detector = HandDetector(staticMode=False, maxHands=1, modelComplexity=1, detectionCon=0.9, minTrackCon=0.5)

# # Global variable for AI response
# ai_output = ""

# def video_stream():
#     """Handles the webcam video streaming with hand gesture recognition and AI integration."""
#     global ai_output
#     cap = cv2.VideoCapture(0)

#     if not cap.isOpened():
#         print("Error: Could not open webcam.")
#         return

#     prev_pos = None
#     canvas = None
#     last_ai_request_time = 0

#     try:
#         while True:
#             success, img = cap.read()
#             if not success:
#                 print("Error: Failed to grab frame.")
#                 break

#             img = cv2.flip(img, 1)

#             # Initialize canvas if necessary
#             if canvas is None or canvas.shape != img.shape:
#                 canvas = np.zeros_like(img)

#             hands, img = detector.findHands(img, draw=True, flipType=True)

#             if hands:
#                 hand = hands[0]
#                 lmList = hand["lmList"]
#                 fingers = detector.fingersUp(hand)

#                 # Reset drawing (All fingers up)
#                 if fingers == [1, 1, 1, 1, 1]:
#                     canvas = np.zeros_like(img)
#                     prev_pos = None

#                 # Drawing gesture (Index finger up)
#                 elif fingers == [0, 1, 0, 0, 0]:
#                     current_pos = tuple(map(int, lmList[8][:2]))  # Index finger tip
#                     if prev_pos is not None:
#                         cv2.line(canvas, prev_pos, current_pos, color=(255, 0, 255), thickness=5)
#                     prev_pos = current_pos

#                 # Eraser gesture (Index and Middle fingers up)
#                 elif fingers == [0, 1, 1, 1, 0]:
#                     current_pos = tuple(map(int, lmList[8][:2]))  # Index finger tip
#                     if prev_pos is not None:
#                         cv2.line(canvas, prev_pos, current_pos, color=(0, 0, 0), thickness=20)
#                     prev_pos = current_pos

#                 else:
#                     prev_pos = None  # Reset when not drawing or erasing

#                 # AI trigger gesture (Thumbs up)
#                 if fingers == [1, 0, 0, 0, 0] and (time.time() - last_ai_request_time > 3):
#                     try:
#                         pil_image = Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))  # Ensure correct format
#                         response = model.generate_content(["Solve this Math problem.", pil_image])
#                         last_ai_request_time = time.time()
                        
#                         # Check if response is valid
#                         if response and hasattr(response, "text"):
#                             ai_output = response.text
#                             print("AI Response:", ai_output)
#                         else:
#                             print("Error: AI response is empty or invalid.")

#                     except Exception as e:
#                         print("Error in AI request:", e)

#             # Overlay drawings on the main image
#             image_combined = cv2.addWeighted(img, 0.6, canvas, 0.4, 0)

#             # Encode frame
#             _, jpeg = cv2.imencode('.jpg', image_combined)
#             frame = jpeg.tobytes()

#             # Stream frame
#             yield (b'--frame\r\n'
#                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

#     except KeyboardInterrupt:
#         print("Video stream stopped.")

#     finally:
#         cap.release()
#         cv2.destroyAllWindows()


# def get_ai_output(request):
#     """Returns the latest AI-generated output as JSON."""
#     return JsonResponse({"output": ai_output})


# def video_feed(request):
#     """Provides the video feed as an HTTP response."""
#     return StreamingHttpResponse(video_stream(), content_type='multipart/x-mixed-replace; boundary=frame')


# def math_solver(request):
#     """Renders the main math solver template."""
#     return render(request, 'math_solver/math_solver.html')


import os
import cv2
import numpy as np
import time
from django.shortcuts import render
from django.http import StreamingHttpResponse, JsonResponse
from cvzone.HandTrackingModule import HandDetector
import google.generativeai as genai
from PIL import Image
from django.http import JsonResponse


def get_ai_output(request):
    return JsonResponse({"output": "AI-generated response here"})


# Load API Key securely
genai.configure(api_key="AIzaSyCW6K9DW9rvuoMJpZAdlBuRMjH6Qg13P7U")
model = genai.GenerativeModel("gemini-1.5-flash")

# Initialize Hand Detector
detector = HandDetector(staticMode=False, maxHands=1, modelComplexity=1, detectionCon=0.9, minTrackCon=0.5)

# Global variables
ai_output = ""
ai_request_sent = False  # Prevent continuous AI requests

def video_stream():
    """Handles the webcam video streaming with hand gesture recognition and AI integration."""
    global ai_output, ai_request_sent
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    prev_pos = None
    canvas = None
    last_ai_request_time = 0

    try:
        while True:
            success, img = cap.read()
            if not success:
                print("Error: Failed to grab frame.")
                break

            img = cv2.flip(img, 1)

            # Initialize canvas if necessary
            if canvas is None or canvas.shape != img.shape:
                canvas = np.zeros_like(img)

            hands, img = detector.findHands(img, draw=True, flipType=True)

            if hands:
                hand = hands[0]
                lmList = hand["lmList"]
                fingers = detector.fingersUp(hand)

                # Reset drawing (All fingers up)
                if fingers == [1, 1, 1, 1, 1]:
                    canvas = np.zeros_like(img)
                    prev_pos = None

                # Drawing gesture (Index finger up)
                elif fingers == [0, 1, 0, 0, 0]:
                    current_pos = tuple(map(int, lmList[8][:2]))  # Index finger tip
                    if prev_pos is not None:
                        cv2.line(canvas, prev_pos, current_pos, color=(255, 0, 255), thickness=5)
                    prev_pos = current_pos

                # Eraser gesture (Index and Middle fingers up)
                elif fingers == [0, 1, 1, 1, 0]:
                    current_pos = tuple(map(int, lmList[8][:2]))  # Index finger tip
                    if prev_pos is not None:
                        cv2.line(canvas, prev_pos, current_pos, color=(0, 0, 0), thickness=20)
                    prev_pos = current_pos

                else:
                    prev_pos = None  # Reset when not drawing or erasing

                # AI trigger gesture (Thumbs up)
                if fingers == [1, 0, 0, 0, 0]:  
                    if not ai_request_sent and (time.time() - last_ai_request_time > 3):
                        try:
                            pil_image = Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))  # Ensure correct format
                            response = model.generate_content(["Solve this Math problem.", pil_image])
                            last_ai_request_time = time.time()
                            ai_request_sent = True  # Set flag to avoid repeated requests

                            # Check if response is valid
                            if response and hasattr(response, "text"):
                                ai_output = response.text
                                print("AI Response:", ai_output)
                            else:
                                print("Error: AI response is empty or invalid.")

                        except Exception as e:
                            print("Error in AI request:", e)

                # Reset the request flag when the user removes the thumbs-up gesture
                else:
                    ai_request_sent = False

            # Overlay drawings on the main image
            image_combined = cv2.addWeighted(img, 0.6, canvas, 0.4, 0)

            # Encode frame
            _, jpeg = cv2.imencode('.jpg', image_combined)
            frame = jpeg.tobytes()

            # Stream frame
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

    except KeyboardInterrupt:
        print("Video stream stopped.")

    finally:
        cap.release()
        cv2.destroyAllWindows()


def get_ai_output(request):
    """Returns the latest AI-generated output as JSON."""
    return JsonResponse({"output": ai_output})


def video_feed(request):
    """Provides the video feed as an HTTP response."""
    return StreamingHttpResponse(video_stream(), content_type='multipart/x-mixed-replace; boundary=frame')


def math_solver(request):
    """Renders the main math solver template."""
    return render(request, 'math_solver/math_solver.html')
