from django.urls import path
from . import views

app_name = 'others'

urlpatterns = [
    path('', views.index, name='others'),
    path('password-generator/', views.password_generator, name='password_generator'),
    path('fortune-teller/', views.fortune_teller, name='fortune_teller'),
    path('number-converter/', views.number_converter, name='number_converter'),
]
