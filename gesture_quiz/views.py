from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse

# def gesture_quiz(request):
#     return render(request, 'gesture_quiz/index.html')

def gesture_quiz(request):
    return JsonResponse({'message': 'Gesture Quiz Coming Soon!'})

