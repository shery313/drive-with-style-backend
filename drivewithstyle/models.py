# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.text import slugify
import random
import string
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
# my custom user model 
class CustomUserManager(BaseUserManager):
    """
    Custom manager for CustomUser to handle email-based authentication.
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    """
    Custom user model where email is the unique identifier for authentication.
    """
    username = None  # Remove the username field
    email = models.EmailField(unique=True, db_index=True)  # Use email as the unique identifier
    

    USERNAME_FIELD = 'email'  # Set email as the unique identifier
    REQUIRED_FIELDS = []  # Remove username from required fields

    objects = CustomUserManager()  # Use the custom manager
   



class Vehicle(models.Model):
    VEHICLE_TYPES = (
        ('Hatchback', 'Hatchback'),
        ('Sedan', 'Sedan'),
        ('SUV', 'SUV'),
        ('Luxury', 'Luxury'),
    )

    TRANSMISSION_CHOICES = (
        ('Automatic', 'Automatic'),
        ('Manual', 'Manual'),
    )

    FUEL_TYPES = (
        ('Petrol', 'Petrol'),
        ('Diesel', 'Diesel'),
        ('Hybrid', 'Hybrid'),
        ('Electric', 'Electric'),
    )

    name = models.CharField(max_length=100)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    description = models.TextField()
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_month = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
    image = models.ImageField(upload_to='vehicles/')
    seats = models.PositiveIntegerField()
    fuel_type = models.CharField(max_length=20, choices=FUEL_TYPES)
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES)
    slug=models.SlugField(unique=True, blank=True)
    rating = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        default=0.0
    )
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Additional features
    air_conditioning = models.BooleanField(default=True)
    luggage_capacity = models.PositiveIntegerField(help_text="Number of bags")
    mileage = models.CharField(max_length=50, blank=True, null=True)
    insurance_coverage = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Fleet"

    def __str__(self):
        return f"{self.name} ({self.vehicle_type})"
    def save(self, *args, **kwargs):
        if not self.slug:
            # Generate a slug from the name
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Booking(models.Model):
    PAYMENT_METHODS = (
        ('bank-transfer', 'Bank Transfer'),
        ('cash', 'Cash on Delivery'),
    )

    BOOKING_STATUS = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    vehicle = models.ForeignKey(
        Vehicle, 
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255, blank=True, null=True)
    pickup_date = models.DateField()
    pickup_time = models.TimeField()
    return_date = models.DateField()
    special_requests = models.TextField(blank=True, null=True)
    
    # Payment information
    payment_method = models.CharField(
        max_length=20, 
        choices=PAYMENT_METHODS,
        default='bank-transfer'
    )
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_proof = models.FileField(
        upload_to='payment_proofs/',
        blank=True,
        null=True
    )
    amount_paid = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        blank=True,
        null=True
    )
    
    # Booking management
    status = models.CharField(
        max_length=20,
        choices=BOOKING_STATUS,
        default='pending'
    )
    booking_reference = models.CharField(
        max_length=20,
        unique=True,
        blank=True
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-pickup_date']
        verbose_name_plural = "Bookings"

    def __str__(self):
        return f"Booking  {self.vehicle.name}"

    def save(self, *args, **kwargs):
        if not self.booking_reference:
            # Generate booking reference on first save
            self.booking_reference = f"PK{timezone.now().strftime('%Y%m%d')}{self.id or 0:04d}".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        super().save(*args, **kwargs)

    @property
    def total_days(self):
        return (self.return_date - self.pickup_date).days

    @property
    def total_cost(self):
        if self.total_days > 0 and self.vehicle:
            return self.total_days * self.vehicle.price_per_day
        return self.vehicle.price_per_day if self.vehicle else 0

class ContactMessage(models.Model):
    SUBJECT_CHOICES = (
        ('general', 'General Inquiry'),
        ('booking', 'Booking Question'),
        ('payment', 'Payment Issue'),
        ('complaint', 'Complaint'),
        ('other', 'Other'),
    )

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES)
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Contact Messages"

    def __str__(self):
        return f"Message from {self.name} - {self.get_subject_display()}"

class Testimonial(models.Model):
    RATING_CHOICES = (
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    )

    customer_name = models.CharField(max_length=100)
    customer_title = models.CharField(max_length=100, blank=True, null=True)
    content = models.TextField()
    rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Testimonials"

    def __str__(self):
        return f"Testimonial from {self.customer_name} ({self.rating} stars)"
    
import logging
logger = logging.getLogger(__name__)


@receiver(post_save, sender=Booking)
def send_booking_emails(sender, instance, created, **kwargs):
    if created:
        try:
            # Customer Email
            subject_customer = f"Booking Confirmation - {instance.booking_reference}"

            html_content_customer = render_to_string(
                "emails/customer_booking_confirmation.html",
                {"booking": instance}
            )

            email_customer = EmailMultiAlternatives(
                subject_customer,
                "",
                settings.DEFAULT_FROM_EMAIL,
                [instance.customer_email],
            )
            email_customer.attach_alternative(html_content_customer, "text/html")
            email_customer.send()

            # Owner Email
            subject_owner = f"New Booking - {instance.booking_reference}"

            html_content_owner = render_to_string(
                "emails/owner_booking_notification.html",
                {"booking": instance}
            )

            email_owner = EmailMultiAlternatives(
                subject_owner,
                "",
                settings.DEFAULT_FROM_EMAIL,
                [settings.OWNER_EMAIL],
            )
            email_owner.attach_alternative(html_content_owner, "text/html")
            email_owner.send()

        except Exception as e:
            logger.error(f"Email sending failed: {str(e)}")