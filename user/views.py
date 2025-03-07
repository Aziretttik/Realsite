from django.contrib.auth.password_validation import password_changed
from django.shortcuts import render, redirect
from .forms import UserRegisterForm
from  django.contrib import messages
from django.contrib.auth import authenticate, login, logout


def user_register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Вы успешно зарегестрировались!')
            return redirect('index')

        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f'{error}')

    form = UserRegisterForm()
    return render(request, 'account/user_register.html', {"form": form})

def user_login_view(request):
    if request.method == 'POST':
        user_email = request.POST['email']
        user_password = request.POST['password']
        user = authenticate(request, username=user_email, password=user_password)

        if user:
            login(request, user)
            messages.success(request, 'вы успешно вошли в систему')
            return redirect('index')

        messages.error(request, 'неверный логин или пароль')

    return render(request, 'account/user_login.html')

def user_logout_view(request):
    logout(request)
    messages.success(request, 'вы успешно вышли из системы')
    return redirect('index')


