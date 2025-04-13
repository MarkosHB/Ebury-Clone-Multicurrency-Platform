from django.contrib import admin
from .models import Client, Currency, Account, AccountCurrency, CurrencyConversion


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'type', 'status', 'registered_at', 'paused_since')
    list_filter = ('type', 'status', 'registered_at')
    search_fields = ('name', 'email', 'city', 'country')


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')
    readonly_fields = ('code', 'name')


@admin.register(CurrencyConversion)
class CurrencyConversionAdmin(admin.ModelAdmin):
    list_display = ('from_currency', 'to_currency', 'rate')
    search_fields = ('from_currency__code', 'to_currency__code')
    readonly_fields = ('from_currency', 'to_currency', 'rate')


class AccountCurrencyInline(admin.TabularInline):
    model = AccountCurrency
    fields = ('currency', 'balance')
    extra = 1


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('client', 'iban', 'swift', 'created_at', 'paused_since')
    list_filter = ('created_at', 'paused_since')
    search_fields = ('iban', 'swift', 'client__name')
    inlines = [AccountCurrencyInline]
