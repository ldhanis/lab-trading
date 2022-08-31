from .models import Order, CurrencyAmount
import django_tables2 as tables

class OrderTable(tables.Table):
    class Meta:
        model = Order
        fields = ("type_of_order" , "direction" , "pair" , "amount" , "fees" , "created_on" )

class CurrencyTable(tables.Table):
    class Meta:
        model = CurrencyAmount
        fields = ("currency" , "amount")   