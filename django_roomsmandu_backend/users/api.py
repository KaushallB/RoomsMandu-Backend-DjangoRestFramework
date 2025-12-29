from django.http import JsonResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes

from .serializers import UserSerializer
from .models import User

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