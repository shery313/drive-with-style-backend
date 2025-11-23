# management/commands/load_fleet_data.py
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from drivewithstyle.models import Vehicle  # Change to your actual app name

class Command(BaseCommand):
    help = 'Load initial fleet data into the database'

    def handle(self, *args, **options):
        fleet_data = [
            # Hatchbacks
            {
                'name': 'Suzuki Alto VXL',
                'vehicle_type': 'Hatchback',
                'price_per_day': 4500,
                'transmission': 'Automatic',
                'seats': 4,
                'fuel_type': 'Petrol',
                'description': 'Compact automatic hatchback perfect for city driving with great fuel efficiency.',
                'luggage_capacity': 2,
                'mileage': '22-24 km/l',
                'air_conditioning': True,
                'insurance_coverage': True,
                'rating': 4.2,
            },
            {
                'name': 'Suzuki Alto VXR',
                'vehicle_type': 'Hatchback', 
                'price_per_day': 42000,
                'transmission': 'Manual',
                'seats': 4,
                'fuel_type': 'Petrol',
                'description': 'Economical manual hatchback for budget-conscious drivers.',
                'luggage_capacity': 2,
                'mileage': '20-22 km/l',
                'air_conditioning': True,
                'insurance_coverage': True,
                'rating': 4.0,
            },
            {
                'name': 'Kia Picanto',
                'vehicle_type': 'Hatchback',
                'price_per_day': 48000,
                'transmission': 'Automatic',
                'seats': 4,
                'fuel_type': 'Petrol',
                'description': 'Stylish and efficient automatic hatchback with modern features.',
                'luggage_capacity': 2,
                'mileage': '18-20 km/l',
                'air_conditioning': True,
                'insurance_coverage': True,
                'rating': 4.3,
            },
            {
                'name': 'Nissan DayZ',
                'vehicle_type': 'Hatchback',
                'price_per_day': 48000,
                'transmission': 'Automatic',
                'seats': 4,
                'fuel_type': 'Petrol',
                'description': 'Compact and reliable automatic hatchback from Nissan.',
                'luggage_capacity': 2,
                'mileage': '19-21 km/l',
                'air_conditioning': True,
                'insurance_coverage': True,
                'rating': 4.1,
            },
            {
                'name': 'Suzuki Cultus VXL',
                'vehicle_type': 'Hatchback',
                'price_per_day': 48000,
                'transmission': 'Automatic',
                'seats': 4,
                'fuel_type': 'Petrol',
                'description': 'Popular automatic hatchback known for its reliability and efficiency.',
                'luggage_capacity': 2,
                'mileage': '20-22 km/l',
                'air_conditioning': True,
                'insurance_coverage': True,
                'rating': 4.4,
            },
            {
                'name': 'Suzuki Cultus VXR',
                'vehicle_type': 'Hatchback',
                'price_per_day': 4500,
                'transmission': 'Manual',
                'seats': 4,
                'fuel_type': 'Petrol',
                'description': 'Manual transmission version of the reliable Cultus hatchback.',
                'luggage_capacity': 2,
                'mileage': '21-23 km/l',
                'air_conditioning': True,
                'insurance_coverage': True,
                'rating': 4.2,
            },
            
            # Sedans
            {
                'name': 'Hyundai Elantra',
                'vehicle_type': 'Sedan',
                'price_per_day': 12000,
                'transmission': 'Automatic',
                'seats': 5,
                'fuel_type': 'Petrol',
                'description': 'Comfortable and stylish sedan with premium features.',
                'luggage_capacity': 3,
                'mileage': '14-16 km/l',
                'air_conditioning': True,
                'insurance_coverage': True,
                'rating': 4.5,
            },
            {
                'name': 'Honda Civic',
                'vehicle_type': 'Sedan',
                'price_per_day': 10000,
                'transmission': 'Automatic',
                'seats': 5,
                'fuel_type': 'Petrol',
                'description': 'Popular sedan known for its performance and reliability.',
                'luggage_capacity': 3,
                'mileage': '13-15 km/l',
                'air_conditioning': True,
                'insurance_coverage': True,
                'rating': 4.6,
            },
            {
                'name': 'Toyota Yaris 1.5',
                'vehicle_type': 'Sedan',
                'price_per_day': 7000,
                'transmission': 'Automatic',
                'seats': 5,
                'fuel_type': 'Petrol',
                'description': 'Fuel-efficient sedan with 1.5L engine for optimal performance.',
                'luggage_capacity': 3,
                'mileage': '16-18 km/l',
                'air_conditioning': True,
                'insurance_coverage': True,
                'rating': 4.3,
            },
            {
                'name': 'Toyota Yaris 1.3',
                'vehicle_type': 'Sedan',
                'price_per_day': 6000,
                'transmission': 'Automatic',
                'seats': 5,
                'fuel_type': 'Petrol',
                'description': 'Economical version of the reliable Yaris sedan.',
                'luggage_capacity': 3,
                'mileage': '17-19 km/l',
                'air_conditioning': True,
                'insurance_coverage': True,
                'rating': 4.2,
            },
            {
                'name': 'Honda City 1.2',
                'vehicle_type': 'Sedan',
                'price_per_day': 6000,
                'transmission': 'Automatic',
                'seats': 5,
                'fuel_type': 'Petrol',
                'description': 'Compact sedan with efficient 1.2L engine.',
                'luggage_capacity': 3,
                'mileage': '15-17 km/l',
                'air_conditioning': True,
                'insurance_coverage': True,
                'rating': 4.1,
            },
            {
                'name': 'Honda City 1.5',
                'vehicle_type': 'Sedan',
                'price_per_day': 7000,
                'transmission': 'Automatic',
                'seats': 5,
                'fuel_type': 'Petrol',
                'description': 'More powerful version of the popular City sedan.',
                'luggage_capacity': 3,
                'mileage': '14-16 km/l',
                'air_conditioning': True,
                'insurance_coverage': True,
                'rating': 4.3,
            },
            
            # SUVs
            {
                'name': 'Haval H6',
                'vehicle_type': 'SUV',
                'price_per_day': 20000,
                'transmission': 'Automatic',
                'seats': 5,
                'fuel_type': 'Petrol',
                'description': 'Modern SUV with advanced features and comfortable interior.',
                'luggage_capacity': 4,
                'mileage': '10-12 km/l',
                'air_conditioning': True,
                'insurance_coverage': True,
                'rating': 4.4,
            },
            {
                'name': 'Hyundai Tucson',
                'vehicle_type': 'SUV',
                'price_per_day': 15000,
                'transmission': 'Automatic',
                'seats': 5,
                'fuel_type': 'Petrol',
                'description': 'Popular SUV known for its style and performance.',
                'luggage_capacity': 4,
                'mileage': '11-13 km/l',
                'air_conditioning': True,
                'insurance_coverage': True,
                'rating': 4.5,
            },
            {
                'name': 'Kia Sportage Alpha',
                'vehicle_type': 'SUV',
                'price_per_day': 15000,
                'transmission': 'Automatic',
                'seats': 5,
                'fuel_type': 'Petrol',
                'description': 'Premium SUV variant with additional features.',
                'luggage_capacity': 4,
                'mileage': '11-13 km/l',
                'air_conditioning': True,
                'insurance_coverage': True,
                'rating': 4.4,
            },
            {
                'name': 'MG HS',
                'vehicle_type': 'SUV',
                'price_per_day': 13000,
                'transmission': 'Automatic',
                'seats': 5,
                'fuel_type': 'Petrol',
                'description': 'British-inspired SUV with modern technology.',
                'luggage_capacity': 4,
                'mileage': '12-14 km/l',
                'air_conditioning': True,
                'insurance_coverage': True,
                'rating': 4.3,
            },
            
            # Luxury
            {
                'name': 'Toyota Land Cruiser V8',
                'vehicle_type': 'Luxury',
                'price_per_day': 260000,
                'transmission': 'Automatic',
                'seats': 7,
                'fuel_type': 'Petrol',
                'description': 'Premium luxury SUV with V8 engine and top-tier features.',
                'luggage_capacity': 6,
                'mileage': '6-8 km/l',
                'air_conditioning': True,
                'insurance_coverage': True,
                'rating': 4.8,
            },
        ]

        created_count = 0
        updated_count = 0

        for vehicle_data in fleet_data:
            # Generate slug if not provided
            if 'slug' not in vehicle_data:
                vehicle_data['slug'] = slugify(vehicle_data['name'])
            
            # Set image to empty string (you'll update later)
            vehicle_data['image'] = ''
            
            vehicle, created = Vehicle.objects.update_or_create(
                name=vehicle_data['name'],
                defaults=vehicle_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Created: {vehicle.name} - Rs. {vehicle.price_per_day}/day')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'🔄 Updated: {vehicle.name} - Rs. {vehicle.price_per_day}/day')
                )

        # Print summary by category
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS("📊 FLEET DATA SUMMARY"))
        self.stdout.write("="*50)
        
        for vehicle_type in ['Hatchback', 'Sedan', 'SUV', 'Luxury']:
            count = Vehicle.objects.filter(vehicle_type=vehicle_type).count()
            self.stdout.write(
                self.style.SUCCESS(f'   {vehicle_type}: {count} vehicles')
            )
            
        self.stdout.write("="*50)
        self.stdout.write(
            self.style.SUCCESS(
                f'🎉 Successfully loaded fleet data! Created: {created_count}, Updated: {updated_count}'
            )
        )
        self.stdout.write(
            self.style.WARNING(
                '📝 Note: Images are set to empty. Update them later in the admin panel.'
            )
        )