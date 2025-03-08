# from django.shortcuts import render

# # Create your views here.
# from django.http import JsonResponse

# def sign_language_recognition(request):
#     return JsonResponse({'message': 'Sign Language Recognition Coming Soon!'})



from django.shortcuts import render
from django.http import JsonResponse
import cv2
from .asl_model import detect_asl

def sign_language_recognition(request):
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
            return JsonResponse({'asl_sign': detected_sign})

    cap.release()
    return JsonResponse({'asl_sign': 'No sign detected'})

def index(request):
    """Render the ASL detection page"""
    return render(request, 'sign_language/index.html')
