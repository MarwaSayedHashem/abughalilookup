from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/search/', views.search_customer, name='search_customer'),
    path('api/generate-sap-code/', views.generate_sap_code, name='generate_sap_code'),
]

