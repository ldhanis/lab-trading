from django.urls import path
from trading_platform import views

urlpatterns = [
	path('dashboard/', views.user_dashboard, name='user_dashboard'),
	path('<str:currency_1_symbol>/<str:currency_2_symbol>', views.trading_dashboard, name='trading_dashboard'),
]