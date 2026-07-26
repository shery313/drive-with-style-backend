from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from .models import Booking, ContactMessage, CustomUser, Promotion, Testimonial, Vehicle, VehicleImage

# Custom User Admin
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

# Vehicle Resources for Import/Export
class VehicleResource(resources.ModelResource):
    class Meta:
        model = Vehicle
        import_id_fields = ['slug']
        fields = ('name', 'vehicle_type', 'price_per_day', 'seats', 'fuel_type', 'transmission', 'is_available')


class VehicleImageInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()

        active_images = 0
        for form in self.forms:
            if not hasattr(form, "cleaned_data") or not form.cleaned_data:
                continue
            if form.cleaned_data.get("DELETE"):
                continue
            if form.cleaned_data.get("image") and form.cleaned_data.get("is_active", True):
                active_images += 1

        if active_images < 3:
            raise ValidationError("Add at least 3 active gallery images for this vehicle.")


class VehicleImageInline(admin.TabularInline):
    model = VehicleImage
    formset = VehicleImageInlineFormSet
    extra = 3
    min_num = 3
    fields = ('image', 'preview', 'alt_text', 'caption', 'sort_order', 'is_active')
    readonly_fields = ('preview',)

    def preview(self, obj):
        if not obj.image:
            return "No image"
        return format_html(
            '<img src="{}" style="height:64px;width:96px;object-fit:cover;border-radius:6px;" />',
            obj.image.url,
        )
    preview.short_description = 'Preview'

# Vehicle Admin
@admin.register(Vehicle)
class VehicleAdmin(ImportExportModelAdmin):
    resource_class = VehicleResource
    list_display = ('name', 'vehicle_type', 'price_per_day', 'seats', 'fuel_type', 'is_available', 'created_at')
    list_filter = ('vehicle_type', 'fuel_type', 'transmission', 'is_available', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at', 'rating')
    list_editable = ('is_available', 'price_per_day')
    inlines = [VehicleImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'vehicle_type', 'description', 'price_per_day', 'image')
        }),
        ('Specifications', {
            'fields': ('seats', 'fuel_type', 'transmission', 'mileage', 'luggage_capacity')
        }),
        ('Features', {
            'fields': ('air_conditioning', 'insurance_coverage', 'rating', 'is_available')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# Booking Admin
@admin.register(Booking)
class BookingAdmin(ImportExportModelAdmin):
    list_display = ('booking_reference', 'customer_name', 'vehicle', 'pickup_date', 'return_date', 'status', 'total_cost')
    list_filter = ('status', 'payment_method', 'pickup_date', 'vehicle__vehicle_type')
    search_fields = ('customer_name', 'customer_email', 'booking_reference', 'vehicle__name')
    readonly_fields = ('booking_reference', 'created_at', 'updated_at', 'total_days', 'total_cost')
    list_editable = ('status',)
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Booking Details', {
            'fields': ('vehicle', 'pickup_location', 'dropoff_location', 'pickup_date', 'pickup_time', 'return_date', 'special_requests')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'transaction_id', 'payment_proof', 'amount_paid')
        }),
        ('Booking Management', {
            'fields': ('status', 'booking_reference', 'notes')
        }),
        ('Calculated Fields', {
            'fields': ('total_days', 'total_cost'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_days(self, obj):
        return obj.total_days
    total_days.short_description = 'Total Days'
    
    def total_cost(self, obj):
        return f"Rs. {obj.total_cost:,.2f}"
    total_cost.short_description = 'Total Cost'

# Contact Message Admin
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_resolved', 'created_at')
    list_filter = ('subject', 'is_resolved', 'created_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_resolved',)
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone', 'subject')
        }),
        ('Message', {
            'fields': ('message',)
        }),
        ('Resolution', {
            'fields': ('is_resolved',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'promotion_type',
        'is_active',
        'is_featured',
        'show_in_announcement_bar',
        'priority',
        'starts_at',
        'ends_at',
        'poster_preview',
    )
    list_filter = (
        'promotion_type',
        'is_active',
        'is_featured',
        'show_in_announcement_bar',
        'audience_region',
        'starts_at',
        'ends_at',
    )
    search_fields = ('title', 'summary', 'description', 'promo_code', 'audience_region')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at', 'poster_preview')
    list_editable = ('is_active', 'is_featured', 'show_in_announcement_bar', 'priority')
    date_hierarchy = 'starts_at'
    actions = ['publish_promotions', 'unpublish_promotions', 'feature_promotions']

    fieldsets = (
        ('Campaign Content', {
            'fields': (
                'title',
                'slug',
                'promotion_type',
                'eyebrow',
                'summary',
                'description',
                'poster',
                'poster_preview',
            )
        }),
        ('Discount & Targeting', {
            'fields': (
                'discount_percent',
                'discount_amount',
                'promo_code',
                'applies_to',
                'audience_region',
                'terms',
            )
        }),
        ('Website Placement', {
            'fields': (
                'cta_label',
                'cta_url',
                'is_featured',
                'show_in_announcement_bar',
                'priority',
            )
        }),
        ('Schedule & Publishing', {
            'fields': ('is_active', 'starts_at', 'ends_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def poster_preview(self, obj):
        if not obj.poster:
            return "No poster"
        return format_html(
            '<img src="{}" style="height:64px;width:96px;object-fit:cover;border-radius:6px;" />',
            obj.poster.url,
        )
    poster_preview.short_description = 'Poster'

    def publish_promotions(self, request, queryset):
        queryset.update(is_active=True)
    publish_promotions.short_description = "Publish selected promotions"

    def unpublish_promotions(self, request, queryset):
        queryset.update(is_active=False)
    unpublish_promotions.short_description = "Unpublish selected promotions"

    def feature_promotions(self, request, queryset):
        queryset.update(is_featured=True)
    feature_promotions.short_description = "Feature selected promotions"

# Testimonial Admin
@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'customer_title', 'rating', 'is_featured')
    list_filter = ('rating', 'is_featured')
    search_fields = ('customer_name', 'content')
    list_editable = ('is_featured',)
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('customer_name', 'customer_title')
        }),
        ('Testimonial Content', {
            'fields': ('content', 'rating', 'is_featured')
        }),
       
    )

# Register Custom User
admin.site.register(CustomUser, CustomUserAdmin)

# Admin Site Customization
admin.site.site_title = "Drive With Style Admin"
admin.site.site_header = "Drive With Style Administration"
admin.site.index_title = "Welcome to Drive With Style Admin Panel"
# Add to admin.py

def mark_as_confirmed(modeladmin, request, queryset):
    queryset.update(status='confirmed')
mark_as_confirmed.short_description = "Mark selected bookings as confirmed"

def mark_as_completed(modeladmin, request, queryset):
    queryset.update(status='completed')
mark_as_completed.short_description = "Mark selected bookings as completed"

def mark_as_resolved(modeladmin, request, queryset):
    queryset.update(is_resolved=True)
mark_as_resolved.short_description = "Mark selected messages as resolved"

def feature_testimonials(modeladmin, request, queryset):
    queryset.update(is_featured=True)
feature_testimonials.short_description = "Feature selected testimonials"

# Add these to the respective admin classes
BookingAdmin.actions = [mark_as_confirmed, mark_as_completed]
ContactMessageAdmin.actions = [mark_as_resolved]
TestimonialAdmin.actions = [feature_testimonials]
