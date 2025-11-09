"""
Authentication URL configuration
"""
from django.urls import path
from .auth import login_view, logout_view, me_view, signup_view

urlpatterns = [
    path('signup', signup_view, name='auth-signup'),
    path('login', login_view, name='auth-login'),
    path('logout', logout_view, name='auth-logout'),
    path('me', me_view, name='auth-me'),
]

