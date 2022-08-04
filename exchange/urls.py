from django.urls import path, include
from exchange import views
urlpatterns = [
    path('' , views.graph )
]