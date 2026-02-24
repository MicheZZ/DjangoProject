from django.urls import path
from . import views

app_name = 'games'

urlpatterns = [
    path('', views.index, name='games'),
    path('guess-number/', views.guess_number, name='guess_number'),
    path('blackjack/', views.blackjack, name='blackjack'),
]
