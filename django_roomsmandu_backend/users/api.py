from django.http import JsonResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import AccessToken

from .serializers import UserSerializer, UserProfileSerializer
from .models import User

from properties.serializers import ReservationsListSerializer

@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def landlord_detail(request, pk):
    try:
        user = User.objects.get(pk=pk)
        serializer = UserSerializer(user, many=False)
        return JsonResponse(serializer.data, safe=False)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    
@api_view(['GET'])
def reservation_list(request):
    reservations = request.user.reservations.all()
    serializer = ReservationsListSerializer(reservations, many=True)
    return JsonResponse(serializer.data, safe=False)


@api_view(['GET', 'PUT'])
def my_profile(request):
    """Get or update current user's profile"""
    try:
        # Get token from header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'No token'}, status=401)
        
        token = AccessToken(auth_header.split('Bearer ')[1])
        user_id = token.payload['user_id']
        user = User.objects.get(pk=user_id)
        
        if request.method == 'GET':
            serializer = UserSerializer(user)
            return JsonResponse(serializer.data)
        
        elif request.method == 'PUT':
            # Update profile fields
            if 'name' in request.data:
                user.name = request.data['name']
            if 'phone_number' in request.data:
                user.phone_number = request.data['phone_number']
            if 'avatar' in request.FILES:
                user.avatar = request.FILES['avatar']
            
            user.save()
            serializer = UserSerializer(user)
            return JsonResponse({'success': True, 'data': serializer.data})
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=400)