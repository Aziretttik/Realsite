from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserRegisterForm
from  django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import OTP, MyUser
from django.core.mail import send_mail
from random import randint


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


def generate_otp():
    random_code = randint(100000, 999999)
    return random_code


def user_login_view(request):
    if request.method == 'POST':
        user_email = request.POST['email']
        user_password = request.POST['password']
        user = authenticate(request, username=user_email, password=user_password)

        if user:
            otp_code = generate_otp()
            otp = OTP(
                user=user,
                code=otp_code
            )
            otp.save()

            send_mail(
                "ваш одноразовый пароль в CYBORG",
                f"Ваш OTP код: {otp_code}",
                "settings.EMAIL_HOST_USER",
                [user_email],
                fail_silently=False,
            )

            messages.success(request, f"одноразовый код отправлен на вашу почту {user_email}")
            return redirect('otp_verify', user.id)

        messages.error(request, 'неверный логин или пароль')

    return render(request, 'account/user_login.html')

def user_logout_view(request):
    logout(request)
    messages.success(request, 'вы успешно вышли из системы')
    return redirect('index')

def opt_verification_view(request, user_id):
    user = get_object_or_404(MyUser, id=user_id)

    if request.method == 'POST':
        otp_code = request.POST.get('otp_code')
        try:
            otp = OTP.objects.filter(
                user=user,
                if_used=False,
                code=otp_code
            ).latest('created_date')

            otp.if_used = True
            otp.save()

            login(request, user)
            messages.success(request, 'вы успешно вошли в систему')
            return redirect('index')

        except OTP.DoesNotExist:
            messages.error(request, 'Неверный код или код уже использован')

    return render(request, 'account/otp_verify.html', {'user': user})

