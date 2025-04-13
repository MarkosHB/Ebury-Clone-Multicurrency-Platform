from django.urls import path

from . import views

urlpatterns = [
    path("homepage", views.homepage, name="homepage"),
    path("", views.user_login, name="user_login"),
]