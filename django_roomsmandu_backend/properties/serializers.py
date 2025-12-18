from rest_framework import serializers

from .models import Property

class PropertyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = (
            'id',
            'title',
            'price_per_month',
            'image_url'
        )