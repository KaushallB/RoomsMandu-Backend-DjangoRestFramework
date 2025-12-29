from django.forms import ModelForm

from .models import Property

class PropertyForm(ModelForm):
    class Meta:
        model=Property
        fields = (
            'title',
            'description',
            'price_per_month',
            'rooms',
            'kitchen',
            'bathrooms',
            'district',
            'category',
            'image'  
            
        )