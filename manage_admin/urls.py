from django.urls import path
from manage_admin import views

urlpatterns = [
    path('create', views.Create , name="Create_data_page"), 
    path('create/exchange', views.CreateExchange, name="Create_Exchange_Post"),
]