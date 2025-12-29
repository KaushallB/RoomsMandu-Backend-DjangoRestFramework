from django.db import models
import uuid
from django.conf import settings
from users.models import User

# Create your models here.
class Property(models.Model):
        id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
        title=models.CharField(max_length=300)
        description=models.TextField()
        price_per_month=models.IntegerField()
        rooms= models.IntegerField()
        kitchen = models.IntegerField(null=True, blank=True)     
        bathrooms = models.IntegerField(null=True, blank=True)
        district=models.CharField(max_length=300)
        category=models.CharField(max_length=300)
        image=models.ImageField(upload_to='uploads/properties')
        landlord=models.ForeignKey(User, related_name='properties', on_delete=models.CASCADE)
        created_at=models.DateTimeField(auto_now_add=True)
    
        def image_url(self):
            return f'{settings.WEBSITE_URL}{self.image.url}'
            
        