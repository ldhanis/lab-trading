from tkinter.messagebox import RETRY
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
    symbol = models.CharField(max_length=64)

    def __str__(self):
        return '{} {}'.format(self.get_exchange_display(), self.name)

    def get_market_value(self, currency_2_symbol):
        return Pair.objects.filter(currency_1=self).get(currency_2__symbol=currency_2_symbol).value

class Pair(models.Model):

    currency_1 = models.ForeignKey(
        Currency, on_delete=models.CASCADE, related_name="currency_1")
    currency_2 = models.ForeignKey(
        Currency, on_delete=models.CASCADE, related_name="currency_2")
    active = models.BooleanField(default=False)
    symbol = models.CharField(max_length=255, default="")
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}/{} ({}{}) - {}'.format(self.currency_1.symbol, self.currency_2.symbol, self.currency_1.name, self.currency_2.name, self.value)

    @property
    def value(self):
        if self.values.last():
            return self.values.last().value
        return 0

    def update_value(self, value):
        pair_value = PairValue()
        pair_value.value = value
        pair_value.pair = self
        pair_value.save()

class PairValue(models.Model):
    pair = models.ForeignKey(Pair, on_delete=models.CASCADE, related_name="values")
    value = models.FloatField(default=0)
    last_updated = models.DateTimeField(auto_now=True)