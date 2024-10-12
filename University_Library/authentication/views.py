from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

def login_page(request):
    template_name = 'authentication/login.html'

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not User.objects.filter(email=email).exists():
            messages.error(request, 'Invalid Email')
            return redirect('login')

        user = authenticate(request, username=email, password=password)

        if user is None:
            messages.error(request, "Invalid Password")
            return redirect('login')
        else:
            login(request, user)
            return redirect('home')

    return render(request, template_name)


def register_page(request):
    template_name = 'authentication/register.html'

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        user_type = request.POST.get('user_type')

        if User.objects.filter(email=email).exists():
            messages.info(request, "Email already taken!")
            return redirect('signup')

        if password1 != password2:
            messages.info(request, "Passwords do not match!")
            return redirect('signup')

        user = User.objects.create_user(
            username=email,  # We're using email as the username
            email=email,
            first_name=first_name,
            last_name=last_name,
        )

        user.set_password(password1)
        user.save()

        # Set the user type
        user.profile.user_type = user_type
        user.profile.save()

        messages.info(request, "Account created successfully!")
        return redirect('login')

    return render(request, template_name)


def logout_view(request):
    logout(request)
    return redirect('login')