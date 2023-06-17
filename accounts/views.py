from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from accounts.forms import UserRegisterForm

from crypto import crypto_arbo
from crypto import crypto_rsa

def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            crypto_arbo.create_folder()
            crypto_arbo.create_files(username)
            crypto_rsa.generate_keys(username)
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            messages.success(
                request, f"Your account has been created and you are now logged in as {username}"
            )
            return redirect("index")
    else:
        form = UserRegisterForm()
    return render(request, "accounts/register.html", {"form": form})

