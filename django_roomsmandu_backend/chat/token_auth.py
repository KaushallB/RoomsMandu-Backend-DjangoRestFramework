from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware

from rest_framework_simplejwt.tokens import AccessToken

from users.models import User


@database_sync_to_async
def get_user(token_key):
    try:
        token = AccessToken(token_key)
        user_id = token.payload['user_id']
        return User.objects.get(pk=user_id)
    except Exception as e:
        return AnonymousUser
    
class TokenAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        self.inner = inner
        
    async def __call__(self,scope,receive,send):
        query_string = scope['query_string'].decode()
        query = {}
        
        if query_string:
            # Parse query parameters safely
            for param in query_string.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    query[key] = value
        
        token_key = query.get('token')
        scope['user'] = await get_user(token_key)
        return await super().__call__(scope,receive,send)