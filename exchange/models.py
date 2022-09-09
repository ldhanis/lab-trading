from django.db import models
from exchange.exchangeApi import krakenApi, noApi

EXCHANGE_CHOICES = [
    ('none', 'No Api'),
    ('krkn', 'Kraken'),
]


class ExchangeApi(models.Model):

    exchange = models.CharField(
        max_length=4, choices=EXCHANGE_CHOICES, default='none')
    authentication = models.JSONField()

    def get_class(self):
        if self.exchange == 'none':
            return noApi.NoAPI(self.authentication)
        elif self.exchange == 'krkn':
            return krakenApi.KrakenAPI(self.authentication)


class Currency(models.Model):

    exchange = models.CharField(
        max_length=4, choices=EXCHANGE_CHOICES, default='none')
    name = models.CharField(max_length=255)
    symbol = models.CharField(max_length=64)

    def __str__(self):
        return '{} {}'.format(self.get_exchange_display(), self.name)

    def get_market_value(self, currency_2_symbol):
        try:
            value = Pair.objects.filter(currency_1=self).get(
                currency_2__symbol=currency_2_symbol).value
        except:
            value = 0
        return value


class Pair(models.Model):

    currency_1 = models.ForeignKey(
        Currency, on_delete=models.CASCADE, related_name="currency_1")
    currency_2 = models.ForeignKey(
        Currency, on_delete=models.CASCADE, related_name="currency_2")
    active = models.BooleanField(default=False)
    symbol = models.CharField(max_length=255, default="")
    last_updated = models.DateTimeField(auto_now=True)
    value = models.FloatField(default=0)

    def __str__(self):
        return '{}/{} ({}{}) - {}'.format(self.currency_1.symbol, self.currency_2.symbol, self.currency_1.name, self.currency_2.name, self.value)

    def update_value(self, value):
        new_value = PairValue()
        new_value.value = value
        new_value.pair = self
        new_value.save()

    @property
    def previous_value(self):
        try:
            return self.values_history.all().order_by('-id')[1].value
        except:
            return 0

    @property
    def value(self):
        try:
            return self.values_history.last().value
        except:
            return 0

    @property
    def krkn_symbol(self):
        return '{}{}'.format(self.currency_1.symbol, self.currency_2.symbol)

    @property
    def krkn_name(self):
        return f'{self.currency_1.name}{self.currency_2.name}'


class PairValue(models.Model):
    pair = models.ForeignKey(
        Pair, on_delete=models.CASCADE, related_name="values_history")
    created_on = models.DateTimeField(auto_now_add=True)
    value = models.FloatField(default=0)
