from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login", views.login_view, name="login"),
    path("login/sent", views.login_sent, name="login_sent"),
    path("login/<str:token>", views.login_verify, name="login_verify"),
    path("logout", views.logout_view, name="logout"),
    path("role/switch", views.switch_role, name="switch_role"),
]
