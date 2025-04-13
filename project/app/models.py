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
    

class CurrencyConversion(models.Model):
    from_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name="from_currency")
    to_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name="to_currency")
    rate = models.DecimalField(max_digits=10, decimal_places=4)

    class Meta:
        unique_together = ('from_currency', 'to_currency')

    def __str__(self):
        return f"{self.from_currency.code} = {self.rate} * {self.to_currency.code}"
    
    
class AccountCurrency(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='account_currencies')
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='account_currencies')
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    class Meta:
        unique_together = ('account', 'currency')

    def __str__(self):
        return f"{self.account.iban} - {self.currency.code}"
    
