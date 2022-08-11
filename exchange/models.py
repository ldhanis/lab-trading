from symtable import Symbol
from django.db import models

class Exchange(models.Model):

    name                    = models.CharField(max_length=255)

class ExchangeApi(models.Model):

    exchange                = models.ForeignKey(Exchange, on_delete=models.CASCADE)
    authentication          = models.JSONField()

class Currency(models.Model):

    name                    = models.CharField(max_length=255)
    exchange                = models.ForeignKey(Exchange, on_delete=models.CASCADE)
    symbol                  = models.CharField(max_length=255 , default="")

class Pair(models.Model):

#    exchange               = models.ForeignKey(Exchange, on_delete=models.CASCADE)
    currency_1              = models.ForeignKey(Currency, on_delete=models.CASCADE , related_name="currency_1")
    currency_2              = models.ForeignKey(Currency, on_delete=models.CASCADE , related_name="currency_2")
    is_active               = models.BooleanField(default = True)
    symbol                  = models.CharField(max_length=255)