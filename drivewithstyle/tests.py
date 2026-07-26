from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from .models import Booking, ContactMessage, Vehicle


TEST_IMAGE = (
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00"
    b"\xff\xff\xff!\xf9\x04\x00\x00\x00\x00\x00,\x00"
    b"\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
)


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="test@example.com",
)
class PublicApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.vehicle = self._create_vehicle("Toyota Yaris")

    def _create_vehicle(self, name):
        return Vehicle.objects.create(
            name=name,
            vehicle_type="Sedan",
            description="Comfortable city sedan",
            price_per_day="8500.00",
            image=SimpleUploadedFile(f"{name}.gif", TEST_IMAGE, content_type="image/gif"),
            seats=4,
            fuel_type="Petrol",
            transmission="Automatic",
            luggage_capacity=2,
        )

    def test_vehicle_slug_generation_is_collision_safe(self):
        second_vehicle = self._create_vehicle("Toyota Yaris")

        self.assertEqual(self.vehicle.slug, "toyota-yaris")
        self.assertEqual(second_vehicle.slug, "toyota-yaris-2")

    def test_public_fleet_is_read_only(self):
        list_response = self.client.get("/api/v1/fleet/")
        create_response = self.client.post(
            "/api/v1/fleet/",
            {
                "name": "Unauthorized Car",
                "vehicle_type": "SUV",
                "description": "Should not be created",
                "price_per_day": "10000.00",
                "seats": 5,
                "fuel_type": "Petrol",
                "transmission": "Automatic",
                "luggage_capacity": 3,
            },
            format="json",
        )

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(create_response.status_code, 403)

    def test_public_booking_create_ignores_admin_only_fields(self):
        response = self.client.post(
            "/api/v1/booking/",
            {
                "vehicle": self.vehicle.id,
                "customer_name": "Test Customer",
                "customer_email": "customer@example.com",
                "customer_phone": "03001234567",
                "pickup_location": "Islamabad",
                "dropoff_location": "Rawalpindi",
                "pickup_date": "2099-01-10",
                "pickup_time": "10:00:00",
                "return_date": "2099-01-11",
                "payment_method": "cash",
                "terms_accepted": True,
                "status": "confirmed",
                "amount_paid": "1.00",
                "notes": "client should not control this",
                "booking_reference": "CLIENTREF123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)

        booking = Booking.objects.get()
        self.assertEqual(booking.status, "pending")
        self.assertIsNone(booking.amount_paid)
        self.assertIsNone(booking.notes)
        self.assertNotEqual(booking.booking_reference, "CLIENTREF123")
        self.assertLessEqual(len(booking.booking_reference), 20)
        self.assertEqual(response.data["booking_reference"], booking.booking_reference)

    def test_public_booking_list_requires_staff(self):
        response = self.client.get("/api/v1/booking/")
        self.assertEqual(response.status_code, 403)

    def test_public_booking_rejects_invalid_dates(self):
        response = self.client.post(
            "/api/v1/booking/",
            {
                "vehicle": self.vehicle.id,
                "customer_name": "Test Customer",
                "customer_email": "customer@example.com",
                "customer_phone": "03001234567",
                "pickup_location": "Islamabad",
                "pickup_date": "2099-01-11",
                "pickup_time": "10:00:00",
                "return_date": "2099-01-10",
                "payment_method": "cash",
                "terms_accepted": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("return_date", response.data)

    def test_public_contact_is_create_only(self):
        post_response = self.client.post(
            "/api/v1/contact/",
            {
                "name": "Curious Customer",
                "email": "hello@example.com",
                "phone": "03001234567",
                "subject": "general",
                "message": "Need details about the fleet.",
            },
            format="json",
        )
        list_response = self.client.get("/api/v1/contact/")

        self.assertEqual(post_response.status_code, 201)
        self.assertEqual(list_response.status_code, 403)
        self.assertEqual(ContactMessage.objects.count(), 1)


@override_settings(
    DEBUG=False,
    SECURE_SSL_REDIRECT=False,
    STORAGES={
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
        },
    },
    JAZZMIN_SETTINGS={
        "site_logo": None,
        "site_icon": None,
        "site_title": "Drive With Style Admin",
        "site_header": "Drive With Style",
        "site_brand": "Drive With Style",
    },
)
class AdminPanelTests(TestCase):
    def test_admin_login_renders_without_static_manifest(self):
        response = self.client.get("/api/v1/admin/login/?next=/api/v1/admin/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Drive With Style")
