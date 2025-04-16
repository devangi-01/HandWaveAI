
import os
import cv2
import time
import numpy as np
import pandas as pd
from playsound import playsound
import threading
from django.shortcuts import render
from django.http import StreamingHttpResponse, JsonResponse
from cvzone.HandTrackingModule import HandDetector
from django.views.decorators.cache import never_cache

# 🔊 Helper functions for playing sounds
def play_selection_sound():
    sound_path = os.path.join(os.path.dirname(__file__), "static", "sound", "select.wav")
    threading.Thread(target=playsound, args=(sound_path,), daemon=True).start()

def play_correct_sound():
    sound_path = os.path.join(os.path.dirname(__file__), "static", "sound", "right.wav")
    threading.Thread(target=playsound, args=(sound_path,), daemon=True).start()

def play_wrong_sound():
    sound_path = os.path.join(os.path.dirname(__file__), "static", "sound", "wrong.wav")
    threading.Thread(target=playsound, args=(sound_path,), daemon=True).start()

def play_gameover_sound():
    sound_path = os.path.join(os.path.dirname(__file__), "static", "sound", "gameover.wav")
    threading.Thread(target=playsound, args=(sound_path,), daemon=True).start()

# 📄 Load CSV file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_FILE_PATH = os.path.join(BASE_DIR, "gesture_quiz", "quiz_questions.csv")

def load_quiz():
    if not os.path.exists(CSV_FILE_PATH):
        print("Error: Quiz questions file not found!")
        return []
    try:
        df = pd.read_csv(CSV_FILE_PATH).dropna()
        df['answer_index'] = pd.to_numeric(df['answer_index'], errors='coerce')
        df = df.dropna().astype({"answer_index": int})
        return [
            {
                "question": row["question"],
                "options": [row["optionA"], row["optionB"], row["optionC"], row["optionD"]],
                "answer_index": int(row["answer_index"]),
            }
            for _, row in df.iterrows()
        ]
    except Exception as e:
        print(f"Error loading quiz: {e}")
        return []

QUIZ_QUESTIONS = load_quiz()

# ✋ Hand detector
detector = HandDetector(
    staticMode=False,
    maxHands=1,
    modelComplexity=1,
    detectionCon=0.75,
    minTrackCon=0.7
)

def get_quiz_state(request):
    return JsonResponse({
        "question_index": request.session.get("question_index", 0),
        "correct_answers": request.session.get("correct_answers", 0),
        "total_questions": len(QUIZ_QUESTIONS)
    })

# 🖼️ Utility to draw centered text
def draw_text_centered(img, text, position, font_scale=1, color=(0, 0, 0), thickness=2):
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0]
    text_x = position[0] - text_size[0] // 2
    text_y = position[1] + text_size[1] // 2
    cv2.putText(img, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)

# 📋 Draw question and options
def draw_quiz_ui(img, question_data, selected_answer):
    img_h, img_w, _ = img.shape
    question_center = (img_w // 2, 120)
    draw_text_centered(img, question_data["question"], question_center, font_scale=1.2, color=(255, 255, 255), thickness=2)
    
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
        
        if selected_answer is not None:
            if i == selected_answer:
                color = (0, 255, 0) if i == correct_index else (0, 0, 255)
            else:
                color = (255, 255, 255)
        else:
            color = (255, 255, 255)
        
        cv2.rectangle(img, (x1, y1), (x2, y2), color, -1)
        draw_text_centered(img, f"{chr(65 + i)}. {option}", ((x1 + x2) // 2, (y1 + y2) // 2), font_scale=0.8, color=(0, 0, 0))
        answer_boxes.append(((x1, y1), (x2, y2)))
    
    return answer_boxes

# 📹 Main quiz webcam logic
def process_frame(request):
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)

    question_index = request.session.get("question_index", 0)
    correct_answers = request.session.get("correct_answers", 0)
    request.session["gameover_played"] = False  # Reset flag
    total_questions = len(QUIZ_QUESTIONS)
    answer_selected = None
    selection_made = False
    last_selection_time = time.time()

    while True:
        success, img = cap.read()
        if not success:
            break

        img = cv2.flip(img, 1)

        if question_index < total_questions:
            answer_boxes = draw_quiz_ui(img, QUIZ_QUESTIONS[question_index], answer_selected)
            hands, _ = detector.findHands(img, draw=True, flipType=True)

            if hands:
                lmList = hands[0]["lmList"]
                fingers_up = detector.fingersUp(hands[0])

                # Count fingers (Index to Pinky) and check if Thumb is up
                num_fingers_up = sum(fingers_up[1:5])  # Index, Middle, Ring, Pinky
                thumb_up = fingers_up[0] == 1  # Thumb

                draw_text_centered(img, f"Fingers Up: {num_fingers_up}", (640, 690), font_scale=1, color=(255, 255, 0), thickness=2)

                # Only allow selection if 1-4 fingers up, and thumb is down
                if num_fingers_up in [1, 2, 3, 4] and not thumb_up and not selection_made:
                    answer_selected = num_fingers_up - 1
                    selection_made = True
                    last_selection_time = time.time()

                    play_selection_sound()

                    if answer_selected == QUIZ_QUESTIONS[question_index]["answer_index"]:
                        correct_answers += 1
                        play_correct_sound()
                    else:
                        play_wrong_sound()

                elif num_fingers_up == 0:
                    answer_selected = None
                    selection_made = False

            if selection_made and time.time() - last_selection_time > 2:
                question_index += 1
                selection_made = False
                answer_selected = None

                request.session["question_index"] = question_index
                request.session["correct_answers"] = correct_answers

        if question_index >= total_questions:
            if not request.session.get("gameover_played", False):
                play_gameover_sound()
                request.session["gameover_played"] = True

            score_percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
            final_img = np.full((800, 1280, 3), 255, dtype=np.uint8)
            draw_text_centered(final_img, "Quiz Over!", (640, 300), font_scale=2, color=(0, 0, 255), thickness=3)
            draw_text_centered(final_img, f"Final Score: {score_percentage:.2f}%", (640, 400), font_scale=1.5, color=(0, 0, 0), thickness=2)
            img = final_img

        _, jpeg = cv2.imencode(".jpg", img)
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + jpeg.tobytes() + b"\r\n\r\n")

    cap.release()


# 🔄 Django views
def video_feed(request):
    return StreamingHttpResponse(process_frame(request), content_type="multipart/x-mixed-replace; boundary=frame")

def get_final_score(request):
    score_percentage = (request.session.get("correct_answers", 0) / len(QUIZ_QUESTIONS)) * 100 if len(QUIZ_QUESTIONS) > 0 else 0
    return JsonResponse({"score": score_percentage})

def gesture_quiz(request):
    return render(request, "gesture_quiz/index.html")

