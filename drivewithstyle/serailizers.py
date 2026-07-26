from django.utils import timezone
from rest_framework import serializers

from .models import Booking, ContactMessage, Promotion, Vehicle, VehicleImage


class PublicVehicleImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleImage
        fields = ("id", "image", "alt_text", "caption", "sort_order")
        read_only_fields = fields


class PublicVehicleSerializer(serializers.ModelSerializer):
    gallery_images = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = (
            "id",
            "slug",
            "name",
            "vehicle_type",
            "description",
            "price_per_day",
            "price_per_month",
            "image",
            "seats",
            "fuel_type",
            "transmission",
            "rating",
            "is_available",
            "air_conditioning",
            "luggage_capacity",
            "mileage",
            "insurance_coverage",
            "gallery_images",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_gallery_images(self, obj):
        images = obj.gallery_images.filter(is_active=True)
        return PublicVehicleImageSerializer(
            images,
            many=True,
            context=self.context,
        ).data


class AdminVehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class PublicBookingSerializer(serializers.ModelSerializer):
    terms_accepted = serializers.BooleanField(write_only=True)
    total_days = serializers.IntegerField(read_only=True)
    total_cost = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = Booking
        fields = (
            "id",
            "vehicle",
            "customer_name",
            "customer_email",
            "customer_phone",
            "pickup_location",
            "dropoff_location",
            "pickup_date",
            "pickup_time",
            "return_date",
            "special_requests",
            "payment_method",
            "transaction_id",
            "payment_proof",
            "booking_reference",
            "created_at",
            "total_days",
            "total_cost",
            "terms_accepted",
        )
        read_only_fields = (
            "id",
            "booking_reference",
            "created_at",
            "total_days",
            "total_cost",
        )

    def validate_vehicle(self, vehicle):
        if not vehicle.is_available:
            raise serializers.ValidationError("This vehicle is currently unavailable.")
        return vehicle

    def validate_payment_proof(self, value):
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Payment proof must be 5 MB or smaller.")

        content_type = getattr(value, "content_type", "")
        if content_type and not content_type.startswith("image/"):
            raise serializers.ValidationError("Payment proof must be an image file.")

        return value

    def validate(self, attrs):
        pickup_date = attrs.get("pickup_date")
        return_date = attrs.get("return_date")
        payment_method = attrs.get("payment_method", "bank-transfer")
        transaction_id = (attrs.get("transaction_id") or "").strip()
        payment_proof = attrs.get("payment_proof")
        terms_accepted = attrs.get("terms_accepted")

        errors = {}

        if not terms_accepted:
            errors["terms_accepted"] = "You must accept the booking terms."

        if pickup_date and pickup_date < timezone.localdate():
            errors["pickup_date"] = "Pickup date cannot be in the past."

        if pickup_date and return_date and return_date < pickup_date:
            errors["return_date"] = "Return date must be on or after the pickup date."

        if payment_method == "bank-transfer":
            if not transaction_id:
                errors["transaction_id"] = "Transaction ID is required for bank transfers."
            if not payment_proof:
                errors["payment_proof"] = "Payment proof is required for bank transfers."
        else:
            attrs["transaction_id"] = ""
            attrs.pop("payment_proof", None)

        if errors:
            raise serializers.ValidationError(errors)

        attrs["dropoff_location"] = attrs.get("dropoff_location") or attrs.get("pickup_location")
        return attrs

    def create(self, validated_data):
        validated_data.pop("terms_accepted", None)
        return super().create(validated_data)


class AdminBookingSerializer(serializers.ModelSerializer):
    total_days = serializers.IntegerField(read_only=True)
    total_cost = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = Booking
        fields = "__all__"
        read_only_fields = ("booking_reference", "created_at", "updated_at", "total_days", "total_cost")


class PublicContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ("id", "name", "email", "phone", "subject", "message", "created_at")
        read_only_fields = ("id", "created_at")


class AdminContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = "__all__"


class PublicPromotionSerializer(serializers.ModelSerializer):
    applies_to_name = serializers.CharField(source="applies_to.name", read_only=True)
    applies_to_slug = serializers.CharField(source="applies_to.slug", read_only=True)
    is_live = serializers.BooleanField(read_only=True)

    class Meta:
        model = Promotion
        fields = (
            "id",
            "slug",
            "title",
            "promotion_type",
            "eyebrow",
            "summary",
            "description",
            "poster",
            "discount_percent",
            "discount_amount",
            "promo_code",
            "applies_to_name",
            "applies_to_slug",
            "audience_region",
            "cta_label",
            "cta_url",
            "terms",
            "starts_at",
            "ends_at",
            "is_featured",
            "show_in_announcement_bar",
            "priority",
            "is_live",
        )
        read_only_fields = fields
