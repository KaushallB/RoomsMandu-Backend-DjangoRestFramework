from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from .models import User


class CustomRegisterSerializer(RegisterSerializer):
    username = None 
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    
    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data['first_name'] = self.validated_data.get('first_name', '')
        data['last_name'] = self.validated_data.get('last_name', '')
        return data
    
    def save(self, request):
        # Get the cleaned data
        first_name = self.validated_data.get('first_name', '')
        last_name = self.validated_data.get('last_name', '')
        email = self.validated_data.get('email', '')
        password = self.validated_data.get('password1', '')
        
        # Combine first and last name for the 'name' field
        name = f"{first_name} {last_name}".strip()
        
        # Create the user
        user = User.objects.create_user(
            email=email,
            name=name,
            password=password
        )
        
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'avatar_url', 'phone_number']


class UserProfileSerializer(serializers.ModelSerializer):
    """For updating user profile"""
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'avatar_url', 'phone_number', 'avatar']
        read_only_fields = ['id', 'email', 'avatar_url']
        

