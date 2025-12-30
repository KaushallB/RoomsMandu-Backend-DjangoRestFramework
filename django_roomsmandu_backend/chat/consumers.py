import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .models import ConversationMessage

class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        
        #Joining Room
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
    async def disconnect(self, close_code):
        #leave room
        
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
    #receive messge from web sockets
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            
            # Check for typing event
            event_type = data.get('event')
            
            if event_type == 'typing':
                # Handle typing indicator - just broadcast, don't save
                name = data.get('name', 'Someone')
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'typing_indicator',
                        'name': name
                    }
                )
                return
            
            # Handle chat messages
            # Check if data is nested under 'data' key
            if 'data' in data:
                message_data = data['data']
            else:
                message_data = data
            
            # Extract data matching the actual frontend structure
            conversation_id = message_data.get('conversation_id')
            body = message_data.get('body')
            name = message_data.get('name', 'Anonymous')
            sent_to_id = message_data.get('sent_to_id')
            created_by_id = message_data.get('created_by_id')
            
            # Broadcast to room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'body': body,
                    'name': name
                }
            )
            
            # Save message
            if conversation_id and body and sent_to_id and created_by_id:
                await self.save_message(conversation_id, body, sent_to_id, created_by_id)
        except Exception as e:
            print(f"Error in receive: {e}")
    
    #sending messages
    
    async def chat_message(self, event):
        body = event['body']
        name = event['name']
        
        await self.send(text_data=json.dumps({
            'body': body,
            'name': name
        }))
    
    # Handle typing indicator
    async def typing_indicator(self, event):
        name = event['name']
        
        await self.send(text_data=json.dumps({
            'event': 'typing',
            'name': name
        }))
        
    
    #store messages
    
    @sync_to_async
    def save_message(self, conversation_id, body, sent_to_id, created_by_id):
        from users.models import User
        
        try:
            created_by = User.objects.get(id=created_by_id)
            ConversationMessage.objects.create(
                conversation_id=conversation_id, 
                body=body, 
                sent_to_id=sent_to_id, 
                created_by=created_by
            )
        except Exception as e:
            print(f"Error saving message: {e}")