from django.urls import path
from manage_admin import views

urlpatterns = [

    # Create Data views

    path('create', views.Create , name="Create_data_page"), 
    path('create/exchange_api', views.CreateExchangeAPI, name="create_exchange_api_post"),
    path('create/currency', views.CreateCurrency, name="create_currency_post"),
    path('create/pair', views.CreatePair, name="create_pair_post"),
    path('create/trading_screen', views.CreateTradingScreen, name="create_trading_screen_post"),
    # Display Data views

    path('display/<str:class_name>' , views.Display , name="display_all_data")
    
    # Update Data Views
    
]