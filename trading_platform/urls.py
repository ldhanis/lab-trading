from django.urls import path
from trading_platform import views

urlpatterns = [
	path('<int:trading_screen_id>/dashboard/', views.user_dashboard, name='user_dashboard'),
	path('<int:trading_screen_id>/<str:currency_1_symbol>/<str:currency_2_symbol>/<str:direction>/', views.create_standard_order, name='standard_order'),
	path('<int:trading_screen_id>/<str:currency_1_symbol>/<str:currency_2_symbol>', views.trading_dashboard, name='trading_dashboard'),

]