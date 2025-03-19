from django.shortcuts import render
from django.http import JsonResponse
import cv2
from .asl_model import detect_asl

def sign_language_recognition(request):
    """Render the ASL recognition page"""
    return render(request, 'sign_language/sign_language.html')

def video_feed(request):
    """Capture webcam video and detect ASL signs"""
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        detected_sign = detect_asl(frame)

        if detected_sign:
            cap.release()
            return JsonResponse({'asl_sign': detected_sign})

    cap.release()
    return JsonResponse({'asl_sign': 'No sign detected'})

def index(request):
    """Render the index page"""
    return render(request, 'sign_language/index.html')
