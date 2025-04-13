import json
from django.core.management.base import BaseCommand
from app.models import Currency, CurrencyConversion

class Command(BaseCommand):
    help = "Populate the Currency and CurrencyConversion models with data from currencies.json"

    def handle(self, *args, **kwargs):
        # Path to the currencies.json file
        file_path = "utils/currencies.json"

        # Load the JSON data
        with open(file_path, "r") as file:
            data = json.load(file)

        # Populate the Currency model
        currencies = {}
        for code, details in data.items():
            name = details["Name"]
            currency, _ = Currency.objects.get_or_create(code=code, defaults={"name": name})
            currencies[code] = currency

        # Populate the CurrencyConversion model
        for from_code, details in data.items():
            from_currency = currencies[from_code]
            conversions = details.get("Conversions", {})
            for to_code, rate in conversions.items():
                to_currency = currencies[to_code]
                CurrencyConversion.objects.get_or_create(
                    from_currency=from_currency,
                    to_currency=to_currency,
                    defaults={"rate": rate}
                )
                
        self.stdout.write(self.style.SUCCESS("Currencies and conversion rates populated successfully."))