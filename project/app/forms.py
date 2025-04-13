from django import forms
from .models import AccountCurrency, Currency

class CurrencyConversionForm(forms.Form):
    from_currency = forms.ModelChoiceField(
        queryset=Currency.objects.none(),
        label="From Currency",
        widget=forms.Select(attrs={"class": "form-select"})
    )
    to_currency = forms.ModelChoiceField(
        queryset=Currency.objects.none(),
        label="To Currency",
        widget=forms.Select(attrs={"class": "form-select"})
    )
    amount = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        label="Amount",
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Enter amount"})
    )

    def __init__(self, account, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit the currency choices to the currencies available in the account
        account_currencies = AccountCurrency.objects.filter(account=account)
        self.fields['from_currency'].queryset = Currency.objects.filter(
            id__in=account_currencies.values_list('currency', flat=True)
        )
        self.fields['to_currency'].queryset = Currency.objects.filter(
            id__in=account_currencies.values_list('currency', flat=True)
        )