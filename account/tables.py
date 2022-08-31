from .models import Order
import django_tables2 as tables

class OrderTable(tables.Table):
    class Meta:
        model = Order
        fields = ("type_of_order" , "direction" , "pair" , "amount" , "fees" , "created_on" )