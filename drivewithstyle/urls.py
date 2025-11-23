from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContactListCreateView,ContactRetrieveUpdateDestroyView,VehicleListCreateView,VehicleRetrieveUpdateDestroyView,BookingListCreateView,BookingRetrieveUpdateDestroyView


urlpatterns = [
   path('fleet/',VehicleListCreateView.as_view(), name='vehicle-list-create'),
   path('fleet/<str:slug>/',VehicleRetrieveUpdateDestroyView.as_view(), name='vehicle-retrieve-update-destroy'),
   path('booking/',BookingListCreateView.as_view(), name='booking-list-create'),
   path('booking/<int:pk>/',BookingRetrieveUpdateDestroyView.as_view(), name='booking-retrieve-update-destroy'),
   path('contact/',ContactListCreateView.as_view(), name='contact-list-create'),
   path('contact/<int:pk>/',ContactRetrieveUpdateDestroyView.as_view(), name='contact-retrieve-update-destroy'),
   
]