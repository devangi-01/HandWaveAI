from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

def combined_login_register_view(request):
    if request.method == 'POST':
        if 'login' in request.POST:
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect('homepage')
            else:
                messages.error(request, "Invalid username or password.")

        elif 'register' in request.POST:
            username = request.POST['username']
            email = request.POST['email']
            password = request.POST['password']
            confirm_password = request.POST['confirm_password']

            if password != confirm_password:
                messages.error(request, "Passwords do not match.")
            elif User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists.")
            elif User.objects.filter(email=email).exists():
                messages.error(request, "Email is already in use.")
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                login(request, user)
                messages.success(request, "Registration successful! You're now logged in.")
                return redirect('homepage')

    return render(request, 'user/login_register.html')
