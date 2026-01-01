from django.http import JsonResponse

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import ConversationSerializer, ConversationDetailSerializer, ConversationMessageSerializer

from .models import Conversation
from users.models import User
import uuid

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def conversation_list(request):
    
    serializer = ConversationSerializer(request.user.conversations.all(), many=True)
    
    return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def convo_detail(request, pk):
    conversation = request.user.conversations.get(pk=pk)
    
    conversation_serializer = ConversationDetailSerializer(conversation, many=False)
    messages_serializer = ConversationMessageSerializer(conversation.messages.all(), many=True)
    
    return JsonResponse({
        'conversation': conversation_serializer.data,
        'messages': messages_serializer.data
    }, safe=False)
    
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def convo_start(request, user_id):
    conversations = Conversation.objects.filter(users__in={user_id}).filter(users__in={request.user.id})
    
    if conversations.count() > 0:
        conversation = conversations.first()
        return JsonResponse({'success': True, 'conversation_id': conversation.id})
    else:
        user = User.objects.get(pk=user_id)
        conversation = Conversation.objects.create()
        conversation.users.add(request.user)
        conversation.users.add(user)
        
        return JsonResponse({'success': True, 'conversation_id': conversation.id})


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def start_instant_call(request, conversation_id):
    """Start an instant video call from chat"""
    try:
        conversation = Conversation.objects.get(pk=conversation_id)
        
        # Verify user is part of conversation
        if request.user not in conversation.users.all():
            return JsonResponse({'error': 'Not authorized'}, status=403)
        
        # Generate unique room name
        room_name = f"RoomsManduChat_{conversation_id}_{uuid.uuid4().hex[:8]}"
        jitsi_url = f'https://jitsi.riot.im/{room_name}'
        
        return JsonResponse({
            'success': True,
            'room_name': room_name,
            'jitsi_url': jitsi_url
        })
    except Conversation.DoesNotExist:
        return JsonResponse({'error': 'Conversation not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)