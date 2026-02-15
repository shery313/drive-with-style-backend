from django.shortcuts import render
from rest_framework.exceptions import ValidationError
import logging
from rest_framework.response import Response
from rest_framework import status


from .serailizers import ContactSerializer,FleetSerializer,BookSerializer
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
from .models import Vehicle,Booking,ContactMessage
import threading
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
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
        logger.debug(f"RAW incoming data: {request.data}")

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

        # Save the booking
        booking_instance = serializer.save(vehicle=vehicle_instance)
        logger.info("Booking created successfully")

        # -----------------------------
        # Send emails asynchronously
        # -----------------------------
        def send_email_async():
            try:
                # Customer Email
                subject_customer = f"Booking Confirmation - {booking_instance.booking_reference}"
                html_customer = render_to_string(
                    "emails/customer_booking_confirmation.html",
                    {"booking": booking_instance}
                )
                email_customer = EmailMultiAlternatives(
                    subject_customer,
                    "",
                    settings.DEFAULT_FROM_EMAIL,
                    [booking_instance.customer_email],
                )
                email_customer.attach_alternative(html_customer, "text/html")
                email_customer.send()

                # Owner Email
                subject_owner = f"New Booking - {booking_instance.booking_reference}"
                html_owner = render_to_string(
                    "emails/owner_booking_notification.html",
                    {"booking": booking_instance}
                )
                email_owner = EmailMultiAlternatives(
                    subject_owner,
                    "",
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.OWNER_EMAIL],
                )
                email_owner.attach_alternative(html_owner, "text/html")
                email_owner.send()

                logger.info("Booking emails sent successfully")
            except Exception as e:
                logger.error(f"Email sending failed: {str(e)}")

        # Start the thread so API responds immediately
        threading.Thread(target=send_email_async).start()

        # Return response immediately
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
