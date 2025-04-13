from django.db import models
from django.contrib.auth.models import User
import utils.constants as constants


class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="client")
    name = models.CharField(max_length=100)
    email = models.EmailField()
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    type = models.CharField(choices=constants.CLIENT_TYPE, max_length=1)
    status = models.CharField(choices=constants.CLIENT_STATUS, max_length=1)
    registered_at = models.DateTimeField(auto_now_add=True)
    paused_since = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class Account(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    iban = models.CharField(max_length=34, unique=True)
    swift = models.CharField(max_length=11, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paused_since = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.iban


class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.code
    

class AccountCurrency(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='account_currencies')
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='account_currencies')
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    class Meta:
        unique_together = ('account', 'currency')

    def __str__(self):
        return f"{self.account.iban} - {self.currency.code}"


class CurrencyConversion(models.Model):
    from_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name="from_currency")
    to_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name="to_currency")
    rate = models.DecimalField(max_digits=10, decimal_places=4)

    def convert(self, amount):
        self.amount = amount
        self.converted_amount = amount * self.rate
        self.save()

        # Update the account balances
        from_account_currency = AccountCurrency.objects.get(account=self.account, currency=self.from_currency)
        to_account_currency = AccountCurrency.objects.get(account=self.account, currency=self.to_currency)

        # Deduct the amount from the from_currency balance
        from_account_currency.balance -= amount
        from_account_currency.save()

        # Add the converted amount to the to_currency balance
        to_account_currency.balance += self.converted_amount
        to_account_currency.save()

        return self.converted_amount
    
    class Meta:
        unique_together = ('from_currency', 'to_currency')

    def __str__(self):
        return f"{self.from_currency.code} = {self.rate} * {self.to_currency.code}"
    
    
class Transaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="conversion_history")
    from_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name="from_conversion_history")
    to_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name="to_conversion_history")
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    converted_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Calculate the converted amount based on the conversion rate
        try:
            conversion = CurrencyConversion.objects.get(
                from_currency=self.from_currency,
                to_currency=self.to_currency
            )
            self.converted_amount = self.amount * conversion.rate

            # Update the account balances
            from_account_currency = AccountCurrency.objects.get(account=self.account, currency=self.from_currency)
            to_account_currency = AccountCurrency.objects.get(account=self.account, currency=self.to_currency)

            # Deduct the amount from the from_currency balance
            if from_account_currency.balance < self.amount:
                raise ValueError("Insufficient balance in the source currency.")

            from_account_currency.balance -= self.amount
            from_account_currency.save()

            # Add the converted amount to the to_currency balance
            to_account_currency.balance += self.converted_amount
            to_account_currency.save()

        except CurrencyConversion.DoesNotExist:
            raise ValueError(f"No conversion rate found for {self.from_currency.code} to {self.to_currency.code}")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.amount} {self.from_currency.code} -> {self.converted_amount} {self.to_currency.code}"
