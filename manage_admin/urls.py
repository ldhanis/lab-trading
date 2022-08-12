from django.urls import path
from manage_admin import views

urlpatterns = [
    path('create', views.Create , name="Create_data_page"), 
    path('create/exchange', views.CreateExchange, name="create_exchange_post"),
    path('create/exchange_api', views.CreateExchangeAPI, name="create_exchange_api_post"),
]