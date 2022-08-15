from django.urls import path
from trading_platform import views

urlpatterns = [
	path('dashboard/', views.user_dashboard, name='trading_dashboard'),
]