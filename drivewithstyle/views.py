import logging
import threading

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.shortcuts import render
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from .models import Booking, ContactMessage, Vehicle
from .serailizers import (
    AdminBookingSerializer,
    AdminContactSerializer,
    AdminVehicleSerializer,
    PublicBookingSerializer,
    PublicContactSerializer,
    PublicVehicleSerializer,
)

logger = logging.getLogger(__name__)


def welcome_page(request):
    current_domain = request.get_host()

    context = {
        "domain": current_domain,
        "admin_url": "/api/v1/admin/",
        "api_url": "/api/",
    }

    return render(request, "welcome.html", context)


def send_booking_emails(booking_id):
    if not settings.DEFAULT_FROM_EMAIL:
        logger.warning("Booking email skipped because DEFAULT_FROM_EMAIL is not configured.")
        return

    try:
        booking = Booking.objects.select_related("vehicle").get(pk=booking_id)

        subject_customer = f"Booking Request Received - {booking.booking_reference}"
        html_customer = render_to_string(
            "emails/customer_booking_confirmation.html",
            {"booking": booking},
        )
        email_customer = EmailMultiAlternatives(
            subject_customer,
            "",
            settings.DEFAULT_FROM_EMAIL,
            [booking.customer_email],
        )
        email_customer.attach_alternative(html_customer, "text/html")
        email_customer.send()

        subject_owner = f"New Booking - {booking.booking_reference}"
        html_owner = render_to_string(
            "emails/owner_booking_notification.html",
            {"booking": booking},
        )
        email_owner = EmailMultiAlternatives(
            subject_owner,
            "",
            settings.DEFAULT_FROM_EMAIL,
            [settings.OWNER_EMAIL],
        )
        email_owner.attach_alternative(html_owner, "text/html")
        email_owner.send()

        logger.info("Booking emails sent successfully for %s", booking.booking_reference)
    except Exception:
        logger.exception("Email sending failed for booking %s", booking_id)


def queue_booking_emails(booking_id):
    email_thread = threading.Thread(
        target=send_booking_emails,
        args=(booking_id,),
        daemon=True,
    )
    email_thread.start()


class VehicleListCreateView(ListCreateAPIView):
    queryset = Vehicle.objects.all()

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        if self.request.method == "GET" and not self.request.user.is_staff:
            return PublicVehicleSerializer
        return AdminVehicleSerializer


class VehicleRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Vehicle.objects.all()
    lookup_field = "slug"

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        if self.request.method == "GET" and not self.request.user.is_staff:
            return PublicVehicleSerializer
        return AdminVehicleSerializer


class BookingListCreateView(ListCreateAPIView):
    queryset = Booking.objects.select_related("vehicle").all()
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_permissions(self):
        if self.request.method == "POST":
            return [AllowAny()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        if self.request.method == "POST" and not self.request.user.is_staff:
            return PublicBookingSerializer
        return AdminBookingSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()

        transaction.on_commit(lambda: queue_booking_emails(booking.pk))

        response_serializer = PublicBookingSerializer(
            booking,
            context=self.get_serializer_context(),
        )
        headers = self.get_success_headers(response_serializer.data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class BookingRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Booking.objects.select_related("vehicle").all()
    serializer_class = AdminBookingSerializer
    permission_classes = [IsAdminUser]


class ContactListCreateView(ListCreateAPIView):
    queryset = ContactMessage.objects.all()

    def get_permissions(self):
        if self.request.method == "POST":
            return [AllowAny()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        if self.request.method == "POST" and not self.request.user.is_staff:
            return PublicContactSerializer
        return AdminContactSerializer


class ContactRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = AdminContactSerializer
    permission_classes = [IsAdminUser]
