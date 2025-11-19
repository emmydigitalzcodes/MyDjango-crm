from django.conf import settings
from django.shortcuts import render, redirect

# Create your views here.
TEMPLATES_DIR = settings.TEMPLATES_DIR


def dashboard_webpage(request, *args, **kwargs):
    print(request.user, request.user.is_authenticated)
    if not request.user.is_authenticated:
        return redirect("/auth/google/login/")
    return render(request, "dashboard/main.html")
