from django.db import models

EXCHANGE_CHOICES = [
    ('none', 'No Api'),
    ('krkn', 'Kraken'),
]


class ExchangeApi(models.Model):

    exchange = models.CharField(
        max_length=4, choices=EXCHANGE_CHOICES, default='none')
    authentication = models.JSONField()


class Currency(models.Model):

    exchange = models.CharField(
        max_length=4, choices=EXCHANGE_CHOICES, default='none')
    name = models.CharField(max_length=255)


class Pair(models.Model):

    currency_1 = models.ForeignKey(
        Currency, on_delete=models.CASCADE, related_name="currency_1")
    currency_2 = models.ForeignKey(
        Currency, on_delete=models.CASCADE, related_name="currency_2")
