from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db import models

from exchange.models import *

from account.manager import UserManager


orders_types = ["market", "limit", "stop-loss", "take-profit",
                "stop-loss-limit", "take-profit-limit", "settle-position"]

class NotEnoughBalance(Exception):
    pass

# Create your models here.


class User(AbstractUser):

    """
    User object
    Represents a person 
    """

    username = None

    email = models.EmailField(_('email address'), unique=True)

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    # Spoken language (FR/NL)
    language_code = models.CharField(max_length=5, default="fr")

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_numer = models.CharField(max_length=15)
    street = models.CharField(max_length=255)
    number = models.CharField(max_length=255)
    box = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=32, default='')
    country_code = models.CharField(max_length=32, default='')

    # Overriding of the base django user
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    @property
    def serialized(self):
        return {
            'email': self.email,
            'language_code': self.language_code
        }

    def __str__(self):
        return self.email


class TradingScreen(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             null=True, blank=True, related_name="trading_screens")
    allowed_pairs = models.ManyToManyField(Pair)
    exchange_api = models.ForeignKey(ExchangeApi, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {}'.format(self.id, self.user)

    def sync_currency_amounts(self):
        trading_api = self.exchange_api.get_class()
        currencies_amounts = trading_api.get_currencies_amounts()

        for symbol, balance in currencies_amounts.items():

            # Try to find CurrencyAmounts linked to this tradingScreen and update it with the API portfolio

            try:

                currency = Currency.objects.filter(
                    exchange=self.exchange_api.exchange).get(symbol=symbol)

                currency_amount, created = CurrencyAmount.objects.get_or_create(
                    currency=currency, trading_screen=self)

                currency_amount.amount = balance
                currency_amount.save()

                print(currency_amount)

            except Exception as e:
                print('\n\n----------------------->', symbol, balance, e)

    def create_order(self, order_type, direction, currency_1_value, currency_2_value, amount_currency_1, limit_price_currency_1=0, trigger_price_currency_1=0):
        api_response = False
        trading_api = self.exchange_api.get_class()

        # Getting Pair
        pair = Pair.objects.filter(currency_1=currency_1_value.currency).get(
            currency_2=currency_2_value.currency)

        order_obj = Order()
        order_obj.type_of_order = order_type
        order_obj.pair = pair
        order_obj.amount = amount_currency_1
        order_obj.trading_screen = self
        order_obj.last_balance = CurrencyAmount.filter(currency = pair.currency_1).last()
        order_obj.save()

        if order_type == 'market':
            # Asking for a market order
            # Checking if trader has enough currency value
            if ((direction == 'buy' and (pair.value * amount_currency_1) <= currency_2_value.amount) or (direction == 'sell' and amount_currency_1 <= currency_1_value.amount)):
                trading_api.market_order(order_obj, pair, direction, amount_currency_1)
            else:
                raise NotEnoughBalance('Not enough Balance')

        self.sync_currency_amounts()


class Order(models.Model):

    type_of_order = models.CharField(max_length=255)
    direction = models.CharField(max_length=255, default="buy")
    pair = models.ForeignKey(Pair, on_delete=models.CASCADE)
    amount = models.FloatField(default=0)  #amount of first pairs
    fees = models.FloatField(default=0)
    trading_screen = models.ForeignKey(TradingScreen, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    fullfilled_on = models.DateTimeField(blank=True, null=True)
    external_id = models.TextField(blank=True, null=True)
    success = models.BooleanField(default=False)
    last_balance = models.FloatField(default=0) # updated quantity of the first currency of this pair

class CurrencyAmount(models.Model):

    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    amount = models.FloatField(default=0)
    trading_screen = models.ForeignKey(
        TradingScreen, null=True, on_delete=models.CASCADE, related_name="currency_amounts")

    def get_value(self, currency_2_symbol):
        if self.currency.symbol == currency_2_symbol:
            return self.amount
        return self.amount * self.currency.get_market_value(currency_2_symbol)

    def __str__(self):
        return '{} {} : {}'.format(self.trading_screen, self.currency, self.amount)
