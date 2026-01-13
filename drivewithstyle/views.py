from django.shortcuts import render
from rest_framework.exceptions import ValidationError
import logging
from rest_framework.response import Response
from rest_framework import status


from .serailizers import ContactSerializer,FleetSerializer,BookSerializer
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
from .models import Vehicle,Booking,ContactMessage

def welcome_page(request):
    # Get the current domain
    current_domain = request.get_host()
    
    context = {
        'domain': current_domain,
        'admin_url': '/api/v1/admin/',
        'api_url': '/api/',
    }
    
    return render(request, 'welcome.html', context)
# Create your views here.
class VehicleListCreateView(ListCreateAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = FleetSerializer

class VehicleRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Vehicle.objects.all()
    serializer_class = FleetSerializer
    lookup_field="slug"
logger = logging.getLogger(__name__)
class BookingListCreateView(ListCreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookSerializer

    def create(self, request, *args, **kwargs):
        logger.debug(f"RAW incoming data: {request.data}")  # See what's being posted

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        vehicle_id = request.data.get('vehicle')
        try:
            vehicle_instance = Vehicle.objects.get(id=vehicle_id)
        except Vehicle.DoesNotExist:
            logger.error(f"Invalid vehicle ID {vehicle_id}")
            return Response({'vehicle': 'Invalid vehicle ID'}, status=400)

        serializer.save(vehicle=vehicle_instance)
        logger.info("Booking created successfully")
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class BookingRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookSerializer

class ContactListCreateView(ListCreateAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactSerializer

class ContactRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactSerializer
