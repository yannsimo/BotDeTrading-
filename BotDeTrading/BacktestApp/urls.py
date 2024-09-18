from django.urls import path
from .views import backtest_view

urlpatterns = [
    path('', backtest_view, name='backtest'),
]
