from django.urls import path
from . import views

urlpatterns = [
    path('hello/', views.TestView.as_view(), name='test'),
]
