from rest_framework.serializers import Serializer, ModelSerializer
from .models import  Vehicle ,ContactMessage,Booking
from rest_framework import serializers
class FleetSerializer(ModelSerializer):
    class Meta:
        model = Vehicle
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'vehicle_type': {'required': True},
            'license_plate': {'required': True},
            'capacity': {'required': True},
            'status': {'required': True},
        }
class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = '__all__'
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'name': {'required': True},
            'email': {'required': True},
            'subject': {'required': True},
            'message': {'required': True},
        }
       