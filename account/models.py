from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db import models
import pytz
from datetime import datetime, date, timedelta
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
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return '{} {}'.format(self.id, self.user)

    def cancel_all_orders(self):
        trading_api = self.exchange_api.get_class()

        for order in Order.objects.filter(trading_screen=self):
            trading_api.cancel_order(order)

        trading_api.cancel_all_orders(Order.objects.filter(trading_screen=self))

    def sync_currency_amounts(self):
        trading_api = self.exchange_api.get_class()
        currencies_amounts = trading_api.get_currencies_amounts()

        for symbol, balance in currencies_amounts.items():

            # Create a currency amount

            try:

                currency = Currency.objects.filter(
                    exchange=self.exchange_api.exchange).get(symbol=symbol)

                currency_amount = CurrencyAmount.objects.create(
                    currency=currency, trading_screen=self, amount=balance)

                print(currency_amount)

            except Exception as e:
                print('\n\n----------------------->', symbol, balance, e)

    def create_order(self, order_type, pair, volume, entry_price, take_profit, stop_loss, currency_1_value, currency_2_value):
        api_response = False
        trading_api = self.exchange_api.get_class()

        # Getting Pair
        pair = Pair.objects.filter(currency_1=currency_1_value.currency).get(
            currency_2=currency_2_value.currency)

        order_obj = Order()

        order_obj.order_type = order_type
        order_obj.pair = pair
        order_obj.volume = volume
        order_obj.entry_price = entry_price
        order_obj.take_profit = take_profit
        order_obj.stop_loss = stop_loss

        order_obj.trading_screen = self

        order_obj.last_balance = CurrencyAmount.objects.filter(trading_screen=self).filter(
            currency=pair.currency_1).last()

        order_obj.save()

        self.sync_currency_amounts()

    def get_pair_price_history(self, pair, date_from, date_to, total_intervals):

        ret_list = []

        # Calculate dates
        time_between = (date_to - date_from) / total_intervals

        for i in range(0, total_intervals + 1):

            date_at = date_from + (time_between * i)

            # Find pair value at that time
            pair_value = PairValue.objects.filter(pair=pair).filter(
                created_on__lte=date_at).order_by('id').last()

            pair_price = pair_value.value if pair_value else 0

            currency_1_amount = CurrencyAmount.objects.filter(trading_screen=self).filter(currency=pair.currency_1).filter(
                created_on__lte=date_at).order_by('id').last()

            currency_2_amount = CurrencyAmount.objects.filter(trading_screen=self).filter(currency=pair.currency_2).filter(
                created_on__lte=date_at).order_by('id').last()
            currency_1_amount_amount = currency_1_amount.amount if currency_1_amount else 0
            currency_1_amount_price = currency_1_amount_amount * pair_price

            ret_list.append(
                {
                    'time': date_at,
                    'pair_price': pair_price,
                    'currency_1_amount': currency_1_amount_amount,
                    'currency_1_amount_price': currency_1_amount_price,
                    'currency_2_amount': currency_2_amount.amount if currency_2_amount else 0
                }
            )

        return ret_list

    def get_currency_amount_history(self, currency, date_from, date_to, total_intervals):
        ret_list = []

        # Calculate dates
        time_between = (date_to - date_from) / total_intervals

        for i in range(0, total_intervals + 1):

            date_at = date_from + (time_between * i)
            currency_amount = CurrencyAmount.objects.filter(trading_screen=self).filter(currency=currency).filter(
                created_on__lte=date_at).order_by('id').last()

            ret_list.append(
                {
                    'time': date_at,
                    'currency_amount': currency_amount.amount if currency_amount else 0
                }
            )
        return ret_list

    def get_portfolio_evolution(self, cryptos, fiat, date_from=datetime.min, date_to=datetime.now()):

        # Passing naive date_from and date_to to aware
        date_from = date_from.replace(tzinfo=pytz.UTC)
        date_to = date_to.replace(tzinfo=pytz.UTC)

        # Getting the first currency_amount of this trading screen to avoid having a date_from that dates before the death of Jesus Christ
        first_currency_amount = CurrencyAmount.objects.filter(
            trading_screen=self).first()
        if first_currency_amount and first_currency_amount.created_on > date_from:
            date_from = first_currency_amount.created_on

        # Getting the first pair_value ever to be sure to have a value over 0
        first_pair_value = PairValue.objects.first()
        if first_pair_value and first_pair_value.created_on > date_from:
            date_from = first_pair_value.created_on

        # Finding pairs
        pairs = self.allowed_pairs.filter(
            currency_1__in=cryptos).filter(currency_2=fiat)

        first_amount = 0
        last_amount = 0

        # Getting fiat value of cryptos
        for pair in pairs:
            pair_history = self.get_pair_price_history(
                pair, date_from, date_to, 1)
            first_amount += pair_history[0]['currency_1_amount_price']
            last_amount += pair_history[1]['currency_1_amount_price']

        fiat_amount_history = self.get_currency_amount_history(
            fiat, date_from, date_to, 1)
        first_amount += fiat_amount_history[0]['currency_amount']
        last_amount += fiat_amount_history[1]['currency_amount']

        return (first_amount, last_amount)

    def new_currency_pair_values(self, pair):
        new_user_currency_1_amount = CurrencyAmount.objects.create(
            currency=pair.currency_1, trading_screen=self)
        new_user_currency_2_amount = CurrencyAmount.objects.create(
            currency=pair.currency_2, trading_screen=self)

        return (new_user_currency_1_amount, new_user_currency_2_amount)
        start_amount += pair_portfolio_history[0]['currency_1_amount_price']


class CurrencyAmount(models.Model):

    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    amount = models.FloatField(default=0)
    created_on = models.DateTimeField(default=datetime.now, blank=True)
    trading_screen = models.ForeignKey(
        TradingScreen, null=True, on_delete=models.CASCADE, related_name="currency_amounts")

    def get_value(self, currency_2_symbol):
        if self.currency.symbol == currency_2_symbol:
            return self.amount
        return self.amount * self.currency.get_market_value(currency_2_symbol)

    def __str__(self):
        return '{} -- {} {} : {}'.format(self.created_on, self.trading_screen, self.currency, self.amount)


class Order(models.Model):

    ORDERS_CHOICES = (
        ('SHORT', 'Short Selling'),
        ('LONG', 'Buy Long')
    )

    order_type = models.CharField(
        max_length=10, choices=ORDERS_CHOICES, default='LONG')
    pair = models.ForeignKey(Pair, on_delete=models.CASCADE)

    volume = models.FloatField(default=0)
    entry_price = models.FloatField(null=True, blank=True)
    take_profit = models.FloatField(null=True, blank=True)
    stop_loss = models.FloatField(null=True, blank=True)
    leverage = models.IntegerField(default=2)

    fees = models.FloatField(default=0)

    trading_screen = models.ForeignKey(TradingScreen, on_delete=models.CASCADE)

    created_on = models.DateTimeField(auto_now_add=True)

    success = models.BooleanField(default=False)

    # OHLC triggers
    # If entry price has been reached, that means that the order has become a position
    position_opened_at = models.DateTimeField(blank=True, null=True)
    position_closed_at = models.DateTimeField(blank=True, null=True)

    order_cancelled_at = models.DateTimeField(blank=True, null=True)

    stop_loss_reached = models.BooleanField(default=False)
    take_profit_reached = models.BooleanField(default=False)

    # updated quantity of the first currency of this pair
    last_balance = models.ForeignKey(
        CurrencyAmount, on_delete=models.SET_NULL, null=True)

    # API related 
    external_data       = models.TextField(null=True, blank=True)

    @property
    def profit_loss(self):

        if not self.position_opened_at:
            return 0

        # Pour calculer votre profit ou votre perte pour une négociation d’achat à long terme, utilisez la formule suivante:

        # PL = S * M * (Ec / E0 - 1) - C, où:

        # PL est votre profit ou perte
        # S est le montant de votre investissement
        # M est la valeur du multiplicateur utilisé
        # Ec est le prix de clôture
        # E0 est le prix d’ouverture
        # C est la commission facturée pour votre transaction

        # Pour calculer votre profit ou perte pour une négociation de vente (Short), utilisez la formule suivante :

        # PL = S * M * (1- Ec / E0) - C

        # https://libertex.com/fr/faq/comment-puis-je-calculer-le-profit

        s = self.volume
        m = self.leverage
        ec = self.take_profit if self.take_profit_reached else self.stop_loss if self.stop_loss_reached else self.pair.value
        e0 = self.entry_price
        c = self.fees

        if self.order_type.lower() == 'short':
            return s * m * (1 - ec / e0) - c
        else:
            return s * m * (ec / e0 - 1) - c

    def handle_creation(self):
        api = self.trading_screen.exchange_api.get_class()
        api.handle_order_creation(self)
        api.handle_stop_loss(self)
        api.handle_take_profit(self)

    def handle_update(self, entry_price, take_profit, stop_loss):
        api = self.trading_screen.exchange_api.get_class()

        if self.position_closed_at:
            raise Exception('Position already closed')
            
        entry_price = entry_price if not self.position_opened_at else None
    

        if api.handle_update(self, entry_price, take_profit, stop_loss):
            self.entry_price = self.entry_price if not entry_price else entry_price
            self.take_profit = take_profit
            self.stop_loss = stop_loss
            self.save()

    def handle_cancel_order(self):
        api = self.trading_screen.exchange_api.get_class()
        api.cancel_order(self)
        # api.get_order_infos(self)