from django.http import JsonResponse

from rest_framework.decorators import api_view

from .serializers import ConversationSerializer

from .models import Conversation

@api_view(['GET'])
def conversation_list(request):
    
    serializer = ConversationSerializer(request.user.conversations.all(), many=True)
    
    return JsonResponse(serializer.data, safe=False)
    