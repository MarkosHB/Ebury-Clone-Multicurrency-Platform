from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Account


def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("homepage")
        else:
            messages.error(request, "Invalid username or password")
            
    return render(request, "login.html")


def user_logout(request):
	logout(request)
	return redirect("login")


def homepage(request):
    client = None
    account = None

    try:
        # Check if the user has an associated client
        client = request.user.client
    except AttributeError:
        messages.error(request, "User is not associated with a client.")

    try:
        # Fetch the single account associated with the client
        account = Account.objects.get(client=client)
    except Account.DoesNotExist:
        messages.error(request, "This client does not have an open account.")

    return render(request, "homepage.html", {"client": client, "account": account})
