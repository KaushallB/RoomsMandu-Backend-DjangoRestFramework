from rest_framework import serializers

from .models import Conversation,ConversationMessage

from users.serializers import UserSerializer

class ConversationMessageSerializer(serializers.ModelSerializer):
    sent_to = UserSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = ConversationMessage
        fields = ('id', 'body', 'sent_to', 'created_by', 'created_at',)

class ConversationSerializer(serializers.ModelSerializer):
    users = UserSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversation
        fields = ('id', 'users', 'modified_at',)

class ConversationDetailSerializer(serializers.ModelSerializer):
    users = UserSerializer(many=True, read_only=True)
    messages = ConversationMessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversation
        fields = ('id', 'users', 'messages', 'modified_at',)
    
class ConversationMessageSerializer(serializers.ModelSerializer):
    sent_to = UserSerializer(many=False, read_only=True)
    created_by = UserSerializer(many=False, read_only=True)
    
    class Meta:
        model = ConversationMessage
        fields = ['id','body','sent_to','created_by']