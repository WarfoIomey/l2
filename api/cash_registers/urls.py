from django.urls import path

from . import views

urlpatterns = [
    path('open-shift', views.open_shift),
]
