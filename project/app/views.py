from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Account, CurrencyConversion
from .forms import CurrencyConversionForm


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


@login_required
def transactions(request, account):
    account = get_object_or_404(Account, id=account.id, client=request.user.client)
    converted_amount = None

    if request.method == "POST":
        form = CurrencyConversionForm(account, request.POST)
        if form.is_valid():
            from_currency = form.cleaned_data['from_currency']
            to_currency = form.cleaned_data['to_currency']
            amount = form.cleaned_data['amount']

            try:
                # Fetch the conversion rate
                conversion = CurrencyConversion.objects.get(
                    from_currency=from_currency,
                    to_currency=to_currency
                )
                converted_amount = conversion.convert(amount)
                messages.success(
                    request,
                    f"{amount} {from_currency.code} = {converted_amount:.2f} {to_currency.code}"
                )
            except CurrencyConversion.DoesNotExist:
                messages.error(request, f"No conversion rate found for {from_currency.code} to {to_currency.code}")
    else:
        form = CurrencyConversionForm(account)

    return render(request, "currency_conversion.html", {
        "account": account,
        "form": form,
        "converted_amount": converted_amount
    })
