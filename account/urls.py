from django.urls import path
from account import views

urlpatterns = [
	path('login/', views.user_login, name='login_page'),
	path('register/', views.user_register, name='register_page'),
	path('logout/', views.user_logout, name='logout_page'),
]