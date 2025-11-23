from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import welcome_page,ContactListCreateView,ContactRetrieveUpdateDestroyView,VehicleListCreateView,VehicleRetrieveUpdateDestroyView,BookingListCreateView,BookingRetrieveUpdateDestroyView


urlpatterns = [
   path('', welcome_page, name='welcome'),
   path('api/v1/fleet/',VehicleListCreateView.as_view(), name='vehicle-list-create'),
   path('api/v1/fleet/<str:slug>/',VehicleRetrieveUpdateDestroyView.as_view(), name='vehicle-retrieve-update-destroy'),
   path('api/v1/booking/',BookingListCreateView.as_view(), name='booking-list-create'),
   path('api/v1/booking/<int:pk>/',BookingRetrieveUpdateDestroyView.as_view(), name='booking-retrieve-update-destroy'),
   path('api/v1/contact/',ContactListCreateView.as_view(), name='contact-list-create'),
   path('api/v1/contact/<int:pk>/',ContactRetrieveUpdateDestroyView.as_view(), name='contact-retrieve-update-destroy'),
   
]