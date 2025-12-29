from rest_framework import serializers

from .models import Property,Reservation

from users.serializers import UserSerializer

class PropertyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = (
            'id',
            'title',
            'price_per_month',
            'image_url'
        )
        
class PropertiesDetailSerializer(serializers.ModelSerializer):
    landlord= UserSerializer(read_only=True, many=False)
    class Meta:
        model = Property
        fields = (
            'id',
            'title',
            'description',
            'price_per_month',
            'image_url',
            'rooms',
            'kitchen',
            'bathrooms',
            'landlord',
            'district',
        )
        
class ReservationsListSerializer(serializers.ModelSerializer):
    property = PropertyListSerializer(read_only=True, many=False)
    
    class Meta:
        model = Reservation
        fields = (
            'id',
            'property',
            'full_name',
            'phone_number',
            'move_in_preference',
            'preferred_move_in_date',
            'num_occupants',
            'status',
            'created_at'
        )