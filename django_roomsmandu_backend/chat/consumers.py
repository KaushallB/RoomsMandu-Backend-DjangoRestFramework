import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .models import ConversationMessage


# ============ SIMPLE NOTIFICATION CONSUMER ============
# Each user connects to their own notification channel
# Other parts of the app can send notifications to this channel

class NotificationConsumer(AsyncJsonWebsocketConsumer):
    """Simple WebSocket for user notifications"""
    
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.group_name = f'notifications_{self.user_id}'
        
        # Join user's notification group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        print(f"User {self.user_id} connected to notifications")
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
    
    # Receive notification and send to WebSocket
    async def notification(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'type': event.get('notification_type', 'info'),
            'url': event.get('url', '')
        }))
    
    # Handle send_notification type (alias for notification)
    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'type': event.get('notification_type', 'info'),
            'url': event.get('url', '')
        }))


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
            
            # Check for event type
            event_type = data.get('event')
            
            if event_type == 'typing':
                # Handle typing indicator - broadcast with user_id
                user_id = data.get('user_id', '')
                name = data.get('name', 'Someone')
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'typing_indicator',
                        'name': name,
                        'user_id': user_id
                    }
                )
                return
            
            if event_type == 'call_request':
                # Someone is calling - send to chat room AND to receiver's global notification
                receiver_id = data.get('receiver_id')
                
                # Send to chat room (for chat page)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'call_event',
                        'event': 'call_request',
                        'caller_id': data.get('caller_id'),
                        'caller_name': data.get('caller_name'),
                        'room_name': data.get('room_name'),
                        'jitsi_url': data.get('jitsi_url')
                    }
                )
                
                # Also send to receiver's global notification channel (for any page)
                if receiver_id:
                    await self.channel_layer.group_send(
                        f'user_calls_{receiver_id}',
                        {
                            'type': 'call_notification',
                            'event': 'incoming_call',
                            'caller_id': data.get('caller_id'),
                            'caller_name': data.get('caller_name'),
                            'room_name': data.get('room_name'),
                            'jitsi_url': data.get('jitsi_url'),
                            'conversation_id': self.room_name
                        }
                    )
                return
            
            if event_type == 'call_accepted':
                # Call was accepted
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'call_event',
                        'event': 'call_accepted',
                        'room_name': data.get('room_name'),
                        'jitsi_url': data.get('jitsi_url')
                    }
                )
                return
            
            if event_type == 'call_declined':
                # Call was declined
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'call_event',
                        'event': 'call_declined'
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
            
            # Save message and send notification
            if conversation_id and body and sent_to_id and created_by_id:
                await self.save_message(conversation_id, body, sent_to_id, created_by_id)
                
                # Send notification to receiver
                await self.channel_layer.group_send(
                    f'notifications_{sent_to_id}',
                    {
                        'type': 'notification',
                        'message': f'New message from {name}',
                        'notification_type': 'info'
                    }
                )
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
        user_id = event.get('user_id', '')
        
        await self.send(text_data=json.dumps({
            'event': 'typing',
            'name': name,
            'user_id': user_id
        }))
    
    # Handle call events (request, accept, decline)
    async def call_event(self, event):
        await self.send(text_data=json.dumps(event))
    
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


class CallConsumer(AsyncJsonWebsocketConsumer):
    """Global consumer for video call notifications - works across all pages"""
    
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.user_group = f'user_calls_{self.user_id}'
        
        # Join user's personal call notification group
        await self.channel_layer.group_add(
            self.user_group,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.user_group,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        event_type = data.get('event')
        
        if event_type == 'call_accepted':
            # Notify the caller that call was accepted
            conversation_id = data.get('conversation_id')
            await self.channel_layer.group_send(
                f'chat_{conversation_id}',
                {
                    'type': 'call_event',
                    'event': 'call_accepted',
                    'jitsi_url': data.get('jitsi_url')
                }
            )
        elif event_type == 'call_declined':
            conversation_id = data.get('conversation_id')
            await self.channel_layer.group_send(
                f'chat_{conversation_id}',
                {
                    'type': 'call_event',
                    'event': 'call_declined'
                }
            )
    
    # Handler for incoming call notification
    async def call_notification(self, event):
        await self.send(text_data=json.dumps(event))