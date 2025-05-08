import os
import cv2
import time
import numpy as np
import pandas as pd
import threading
import json
from django.shortcuts import render, redirect
from django.http import StreamingHttpResponse, JsonResponse
from cvzone.HandTrackingModule import HandDetector
from django.views.decorators.cache import never_cache
from django.http import HttpResponseRedirect
import random

# Constants for better code organization
CONFIDENCE_THRESHOLD = 0.9
MIN_TRACKING_CONFIDENCE = 0.8
SELECTION_DELAY = 1.5  # Increased delay for more accurate selections
GESTURE_STABILITY_FRAMES = 5  # Number of frames to confirm a gesture

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_FILE_PATH = os.path.join(BASE_DIR, "gesture_quiz", "quiz_questions.csv")

def restart_quiz(request):
    """Reset the quiz session and redirect to the quiz page"""
    request.session.flush()
    return HttpResponseRedirect('/quiz')

def sanitize_text(text):
    """Clean text for display"""
    if not isinstance(text, str):
        return str(text)
    return text.replace("×", "x").replace("÷", "/")

def load_quiz():
    """Load and validate quiz questions from CSV file"""
    if not os.path.exists(CSV_FILE_PATH):
        print("❌ Quiz file not found at:", CSV_FILE_PATH)
        return []
    
    try:
        df = pd.read_csv(CSV_FILE_PATH).dropna()
        # Ensure answer_index is numeric and valid
        df["answer_index"] = pd.to_numeric(df["answer_index"], errors="coerce")
        df = df.dropna().astype({"answer_index": int})
        
        # Validate answer indices are within range (0-3)
        df = df[df["answer_index"].between(0, 3)]
        
        if len(df) < 10:
            print(f"⚠️ Warning: Only {len(df)} valid questions found. Need at least 10.")
            return list(df.iterrows())
            
        # Select 10 random questions
        random_questions = random.sample(list(df.iterrows()), 10)
        
        return [
            {
                "question": sanitize_text(row["question"]),
                "options": [
                    sanitize_text(row["optionA"]), 
                    sanitize_text(row["optionB"]), 
                    sanitize_text(row["optionC"]), 
                    sanitize_text(row["optionD"])
                ],
                "answer_index": int(row["answer_index"]),
            }
            for _, row in random_questions
        ]
    except Exception as e:
        print(f"❌ Error loading quiz: {e}")
        return []

# Load quiz questions once at module level
QUIZ_QUESTIONS = load_quiz()

# Initialize hand detector with improved parameters
detector = HandDetector(
    staticMode=False,
    maxHands=1,
    modelComplexity=1,
    detectionCon=CONFIDENCE_THRESHOLD,
    minTrackCon=MIN_TRACKING_CONFIDENCE
)

def get_quiz_state(request):
    """Return current quiz state as JSON"""
    question_index = request.session.get("question_index", 0)
    correct_answers = request.session.get("correct_answers", 0)
    total_questions = len(QUIZ_QUESTIONS)
    
    # Calculate accurate percentage
    score_percentage = 0
    if total_questions > 0 and question_index > 0:
        score_percentage = (correct_answers / question_index) * 100
        
    return JsonResponse({
        "question_index": question_index,
        "correct_answers": correct_answers,
        "total_questions": total_questions,
        "current_score": round(score_percentage, 1)
    })

def draw_text_centered(img, text, position, font_scale=1, color=(0, 0, 0), thickness=2):
    """Draw centered text on image"""
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0]
    text_x = position[0] - text_size[0] // 2
    text_y = position[1] + text_size[1] // 2
    cv2.putText(img, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)

def draw_quiz_ui(img, question_data, selected_answer, confidence=0):
    """Draw quiz UI elements on the image"""
    img_h, img_w, _ = img.shape
    
    # Draw question
    question_center = (img_w // 2, 120)
    question_text = sanitize_text(question_data["question"])
    # Add background for better readability
    text_size = cv2.getTextSize(question_text, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 4)[0]
    cv2.rectangle(img, 
                 (question_center[0] - text_size[0]//2 - 10, question_center[1] - text_size[1] - 10),
                 (question_center[0] + text_size[0]//2 + 10, question_center[1] + 10),
                 (255, 255, 255), -1)
    draw_text_centered(img, question_text, question_center, font_scale=1.2, color=(0, 0, 0), thickness=4)

    # Draw answer boxes
    answer_boxes = []
    box_width, box_height = 260, 70
    gap_x, gap_y = 40, 80
    start_x = (img_w - (2 * box_width + gap_x)) // 2
    start_y = 200

    correct_index = question_data["answer_index"]

    for i, option in enumerate(question_data["options"]):
        row, col = divmod(i, 2)
        x1 = start_x + col * (box_width + gap_x)
        y1 = start_y + row * (box_height + gap_y)
        x2, y2 = x1 + box_width, y1 + box_height

        # Determine box color based on selection state
        if selected_answer is not None:
            if i == selected_answer:
                color = (0, 255, 0) if i == correct_index else (0, 0, 255)
                # Add confidence indicator
                cv2.rectangle(img, (x1, y2 + 5), (x1 + int(box_width * confidence), y2 + 15), (255, 165, 0), -1)
            else:
                color = (255, 255, 255)
        else:
            color = (255, 255, 255)

        # Draw option box
        cv2.rectangle(img, (x1, y1), (x2, y2), color, -1)
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 0), 2)  # Border for better visibility
        
        # Draw option text
        option_text = f"{chr(65 + i)}. {sanitize_text(option)}"
        draw_text_centered(img, option_text, ((x1 + x2) // 2, (y1 + y2) // 2), font_scale=0.8, color=(0, 0, 0))
        
        answer_boxes.append(((x1, y1), (x2, y2)))

    # Draw gesture confidence indicator
    if selected_answer is not None:
        cv2.putText(img, f"Confidence: {confidence:.2f}", (50, img_h - 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    return answer_boxes

def process_frame(request):
    """Process video frames and handle quiz logic"""
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)

    # Initialize quiz state from session
    question_index = request.session.get("question_index", 0)
    correct_answers = request.session.get("correct_answers", 0)
    request.session["gameover_played"] = False
    total_questions = len(QUIZ_QUESTIONS)
    
    # Gesture detection state
    answer_selected = None
    selection_made = False
    last_selection_time = time.time()
    
    # Gesture stability tracking
    gesture_history = []
    gesture_confidence = 0.0
    
    try:
        while True:
            success, img = cap.read()
            if not success:
                print("Failed to capture frame from camera")
                break

            img = cv2.flip(img, 1)  # Mirror image for intuitive interaction

            if question_index < total_questions:
                # Draw quiz UI
                answer_boxes = draw_quiz_ui(img, QUIZ_QUESTIONS[question_index], answer_selected, gesture_confidence)
                
                # Detect hands with improved parameters
                hands, img = detector.findHands(img, draw=True, flipType=True)

                if hands:
                    # Get hand landmarks and finger status
                    lmList = hands[0]["lmList"]
                    fingers_up = detector.fingersUp(hands[0])
                    
                    # Count fingers (excluding thumb)
                    num_fingers_up = sum(fingers_up[1:5])
                    thumb_up = fingers_up[0] == 1
                    
                    # Display finger count
                    cv2.putText(img, f"Fingers Up: {num_fingers_up}", (50, 690), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                    
                    # Track gesture stability
                    gesture_history.append(num_fingers_up)
                    if len(gesture_history) > GESTURE_STABILITY_FRAMES:
                        gesture_history.pop(0)
                    
                    # Only consider stable gestures (same gesture for multiple frames)
                    if len(gesture_history) == GESTURE_STABILITY_FRAMES:
                        most_common = max(set(gesture_history), key=gesture_history.count)
                        stability = gesture_history.count(most_common) / len(gesture_history)
                        
                        # Update gesture confidence
                        gesture_confidence = stability
                        
                        # Process valid gestures (1-4 fingers, no thumb)
                        if most_common in [1, 2, 3, 4] and not thumb_up and stability > 0.6 and not selection_made:
                            answer_selected = most_common - 1
                            selection_made = True
                            last_selection_time = time.time()
                            
                            # Check if answer is correct
                            if answer_selected == QUIZ_QUESTIONS[question_index]["answer_index"]:
                                correct_answers += 1
                    
                    # Reset selection if hand forms a fist (no fingers up)
                    elif num_fingers_up == 0 and sum(fingers_up) == 0:
                        answer_selected = None
                        selection_made = False
                        gesture_history = []
                
                # Move to next question after delay
                if selection_made and time.time() - last_selection_time > SELECTION_DELAY:
                    question_index += 1
                    selection_made = False
                    answer_selected = None
                    gesture_history = []
                    gesture_confidence = 0.0

                    # Update session
                    request.session["question_index"] = question_index
                    request.session["correct_answers"] = correct_answers
            
            # Show final score when quiz is complete
            if question_index >= total_questions:
                if not request.session.get("gameover_played", False):
                    request.session["gameover_played"] = True

                # Calculate accurate score percentage
                score_percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
                
                # Create final score display
                final_img = np.full((800, 1280, 3), 255, dtype=np.uint8)
                
                # Draw decorative elements
                cv2.rectangle(final_img, (0, 0), (1280, 100), (99, 102, 241), -1)  # Header
                cv2.rectangle(final_img, (0, 700), (1280, 800), (99, 102, 241), -1)  # Footer
                
                # Draw quiz results
                draw_text_centered(final_img, "Quiz Complete!", (640, 300), font_scale=2, color=(0, 0, 255), thickness=3)
                draw_text_centered(final_img, f"Final Score: {score_percentage:.1f}%", (640, 400), font_scale=1.5, color=(0, 0, 0), thickness=2)
                draw_text_centered(final_img, f"Correct Answers: {correct_answers} out of {total_questions}", (640, 500), font_scale=1.2, color=(0, 0, 0), thickness=2)
                
                # Add feedback message based on score
                if score_percentage >= 80:
                    message = "Excellent! You're a gesture quiz master!"
                elif score_percentage >= 60:
                    message = "Great job! You've got good gesture skills!"
                elif score_percentage >= 40:
                    message = "Good effort! Keep practicing!"
                else:
                    message = "Nice try! Practice makes perfect!"
                
                draw_text_centered(final_img, message, (640, 600), font_scale=1, color=(0, 0, 0), thickness=2)
                
                img = final_img

            # Convert frame to JPEG
            _, jpeg = cv2.imencode(".jpg", img)
            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + jpeg.tobytes() + b"\r\n\r\n")

    except Exception as e:
        print(f"Error in video processing: {e}")
    finally:
        cap.release()

def video_feed(request):
    """Stream processed video frames"""
    return StreamingHttpResponse(process_frame(request), content_type="multipart/x-mixed-replace; boundary=frame")

def get_final_score(request):
    """Return final quiz score as JSON"""
    correct_answers = request.session.get("correct_answers", 0)
    total_questions = len(QUIZ_QUESTIONS)
    score_percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    
    # Add more detailed results
    return JsonResponse({
        "score": round(score_percentage, 1),
        "correct_answers": correct_answers,
        "total_questions": total_questions,
        "message": get_score_message(score_percentage)
    })

def get_score_message(score):
    """Return appropriate message based on score"""
    if score >= 80:
        return "Excellent! You're a gesture quiz master!"
    elif score >= 60:
        return "Great job! You've got good gesture skills!"
    elif score >= 40:
        return "Good effort! Keep practicing!"
    else:
        return "Nice try! Practice makes perfect!"

def gesture_quiz(request):
    """Render the quiz page"""
    # Reset quiz state if requested
    if request.GET.get('restart', False):
        request.session["question_index"] = 0
        request.session["correct_answers"] = 0
        request.session["gameover_played"] = False
    
    return render(request, "gesture_quiz/index.html")