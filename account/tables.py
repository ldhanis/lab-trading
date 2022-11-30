from .models import Order, CurrencyAmount
import django_tables2 as tables


class OrderTable(tables.Table):
    class Meta:
        model = Order
        fields = ("created_on", "order_type", "volume", "entry_price", "take_profit", "stop_loss", "fees",
                  "position_opened_at", "position_closed_at", "order_cancelled_at", "stop_loss_reached", "take_profit_reached", "profit_loss")


class CurrencyTable(tables.Table):
    class Meta:
        model = CurrencyAmount
        fields = ("currency", "amount")
