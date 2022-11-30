from django.urls import path
from trading_platform import views

urlpatterns = [
	path('<int:trading_screen_id>/dashboard/', views.user_dashboard, name='user_dashboard'),
	
	path('<int:trading_screen_id>/cancel-all/', views.cancel_all_orders, name='cancel_all_orders'),
	path('<int:trading_screen_id>/sync-amounts/', views.sync_amounts, name='sync_amounts'),

    path('updateOrder/', views.update_order, name='update_order'),
    path('cancelOrder/<int:order_id>', views.cancel_order, name='cancel_order'),
    
	path('<int:trading_screen_id>/<str:currency_1_symbol>/<str:currency_2_symbol>/order/', views.create_order, name='create_order'),
	path('<int:trading_screen_id>/<str:currency_1_symbol>/<str:currency_2_symbol>', views.trading_dashboard, name='trading_dashboard'),

]