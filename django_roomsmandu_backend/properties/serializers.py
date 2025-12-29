from rest_framework import serializers

from .models import Property

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
