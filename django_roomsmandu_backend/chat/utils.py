"""
Simple notification helper.
Use this to send notifications to any user from anywhere in Django.
"""

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def send_notification(user_id, message, notification_type='info'):
    """
    Send a notification to a user's browser.
    
    Args:
        user_id: The user's ID (string or int)
        message: The notification message
        notification_type: 'info', 'success', 'error', or 'call'
    
    Example:
        send_notification(user.id, "You have a new message!", "info")
    """
    channel_layer = get_channel_layer()
    
    async_to_sync(channel_layer.group_send)(
        f'notifications_{user_id}',
        {
            'type': 'notification',  # This calls the notification method in consumer
            'message': message,
            'notification_type': notification_type
        }
    )
