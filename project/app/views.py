import json
from decimal import Decimal

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.http import JsonResponse

from .models import Account, CurrencyConversion, Transaction


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


@csrf_exempt
@login_required
def transactions(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            from_currency_code = data.get("from_currency")
            to_currency_code = data.get("to_currency")

            # Convert amount to Decimal to ensure compatibility with conversion rate
            amount = Decimal(data.get("amount"))

            # Fetch the account for the logged-in user
            account = Account.objects.get(client=request.user.client)

            # Fetch the conversion rate
            conversion = CurrencyConversion.objects.get(
                from_currency__code=from_currency_code,
                to_currency__code=to_currency_code
            )

            # Perform the conversion and create a transaction
            converted_amount = amount * conversion.rate
            transaction = Transaction.objects.create(
                account=account,
                from_currency=conversion.from_currency,
                to_currency=conversion.to_currency,
                amount=amount,
                converted_amount=converted_amount
            )

            return JsonResponse({
                "success": True,
                "converted_amount": round(transaction.converted_amount, 2),
                "to_currency": to_currency_code
            })
        except CurrencyConversion.DoesNotExist:
            return JsonResponse({"success": False, "error": "Conversion rate not found."})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request method."})
