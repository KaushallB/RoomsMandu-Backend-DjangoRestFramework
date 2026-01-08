from rest_framework import serializers

from .models import Property, Reservation, VideoCallSchedule

from users.serializers import UserSerializer

class PropertyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = (
            'id',
            'title',
            'price_per_month',
            'image_url',
            'district',
            'address',
            'is_available'
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
            'latitude',
            'longitude',
            'address',
            'is_available',
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
            'message',
            'status',
            'created_at'
        )


class VideoCallScheduleSerializer(serializers.ModelSerializer):
    property = PropertyListSerializer(read_only=True, many=False)
    tenant = UserSerializer(read_only=True, many=False)
    landlord = UserSerializer(read_only=True, many=False)
    jitsi_url = serializers.SerializerMethodField()
    
    class Meta:
        model = VideoCallSchedule
        fields = (
            'iSd',
            'property',
            'tenant',
            'landlord',
            'scheduled_time',
            'status',
            'jitsi_url',
            'created_at'
        )
    
    def get_jitsi_url(self, obj):
        return obj.get_jitsi_url()