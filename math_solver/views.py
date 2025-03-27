import os
import cv2
import numpy as np
import time
from django.shortcuts import render
from django.http import StreamingHttpResponse, JsonResponse
from cvzone.HandTrackingModule import HandDetector
import google.generativeai as genai
from PIL import Image
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage

# Load API Key securely
genai.configure(api_key="AIzaSyCW6K9DW9rvuoMJpZAdlBuRMjH6Qg13P7U")
model = genai.GenerativeModel("gemini-1.5-flash")

# Initialize Hand Detector
detector = HandDetector(staticMode=False, maxHands=1, modelComplexity=1, detectionCon=0.9, minTrackCon=0.5)

# Global variables
ai_output = ""
ai_request_sent = False  # Prevent repeated AI requests
thumbs_up_active = False  # Track thumbs-up activation


def video_stream():
    """Handles the webcam video streaming with hand gesture recognition and AI integration."""
    global ai_output, ai_request_sent, thumbs_up_active
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FPS, 45)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    prev_pos = None
    canvas = None

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

                # if hands:
                #     hand = hands[0]
                #     bbox = hand["bbox"]  # [x, y, w, h]
                #     x, y, w, h = bbox
                
                #     # Correct hand type after flipping
                #     hand_type = "Left" if hand["type"] == "Right" else "Right"
                
                #     # Draw box around hand
                #     cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                #     # Add text for hand type
                #     cv2.putText(img, f'{hand_type} Hand', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)


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
                    if not ai_request_sent and not thumbs_up_active:
                        thumbs_up_active = True  # Mark that thumbs-up is held
                        try:
                            pil_image = Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))  # Ensure correct format
                            response = model.generate_content(["Solve this Math problem.", pil_image])
                            ai_request_sent = True  # Set flag to avoid repeated requests

                            # Check if response is valid
                            if response and hasattr(response, "text"):
                                ai_output = response.text
                                print("AI Response:", ai_output)
                            else:
                                print("Error: AI response is empty or invalid.")

                        except Exception as e:
                            print("Error in AI request:", e)

                else:
                    # Reset AI request flag when the user lowers their thumb
                    thumbs_up_active = False
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

def upload_math_problem(request):
    """Handles image upload and sends it to Gemini AI for solving."""
    if request.method == "POST" and request.FILES.get("math_image"):
        try:
            # Save uploaded image
            uploaded_image = request.FILES["math_image"]
            image_path = default_storage.save("uploads/" + uploaded_image.name, uploaded_image)

            # Convert image to PIL format
            pil_image = Image.open(default_storage.path(image_path))

            # Send to AI for solving
            response = model.generate_content(["Solve this Math problem shown in the image.", pil_image])

            # Check if AI response is valid
            if response and hasattr(response, "text"):
                ai_solution = response.text
            else:
                ai_solution = "AI could not generate a solution."

            return JsonResponse({"solution": ai_solution})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)

def get_ai_output(request):
    """Returns the latest AI-generated output as JSON."""
    return JsonResponse({"output": ai_output})


def video_feed(request):
    """Provides the video feed as an HTTP response."""
    return StreamingHttpResponse(video_stream(), content_type='multipart/x-mixed-replace; boundary=frame')


def math_solver(request):
    """Renders the main math solver template."""
    return render(request, 'math_solver/math_solver.html')
