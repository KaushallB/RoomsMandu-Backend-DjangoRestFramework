from django.http import JsonResponse

from rest_framework.decorators import api_view,authentication_classes,permission_classes
from .models import Property, Reservation
from .serializers import PropertyListSerializer, PropertiesDetailSerializer
from .forms import PropertyForm
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.permissions import IsAuthenticated
from users.models import User


@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def properties_list(request):
    #Auth
    
    try:
        token = request.META['HTTP_AUTHORIZATION'].split('Bearer ')[1]
        token = AccessToken(token)
        user_id = token.payload['user_id']
        user = User.objects.get(pk=user_id)   
    except Exception as e:
        user = None 
        
        
    favourites = []
    landlord_id = request.GET.get('landlord_id', None)
    
    if landlord_id:
        properties = Property.objects.filter(landlord_id=landlord_id)
    else:
        properties = Property.objects.all()
    
    #favourite
    if user:
        for property in properties:
            if user in property.favourite.all():
                favourites.append(property.id)
                
    serializer = PropertyListSerializer(properties, many=True)
    
    return JsonResponse({
        'data': serializer.data,
        'favourites': favourites
    })
    
@api_view(['POST', 'FILES'])
def create_property(request):
    form = PropertyForm(request.POST, request.FILES)
    
    if form.is_valid():
        property = form.save(commit=False)
        property.landlord=request.user
        property.save()
        
        return JsonResponse({'success': True})
    else:
        print('ERROR', form.errors, form.non_field_errors)
        return JsonResponse({'Errors': form.errors.as_json()},status=400)
    
    
@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def properties_details(request, pk):
    property = Property.objects.get(pk=pk)
    
    serializer = PropertiesDetailSerializer(property, many=False)
    
    return JsonResponse(serializer.data)
    
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def book_property(request, pk):
    try:
        move_in_preference = request.POST.get('move_in_preference', '')
        preferred_move_in_date = request.POST.get('preferred_move_in_date', '')
        num_occupants= request.POST.get('num_occupants', '')
        full_name = request.POST.get('full_name', '')
        phone_number = request.POST.get('phone_number', '')
        message = request.POST.get('message', '')
        
        # Validate required fields
        if not all([move_in_preference, num_occupants, full_name, phone_number]):
            return JsonResponse({'success': False, 'error': 'Missing required fields'}, status=400)
        
        property = Property.objects.get(pk=pk)
        
        Reservation.objects.create(
            property=property,
            move_in_preference=move_in_preference,
            preferred_move_in_date=preferred_move_in_date,
            num_occupants=num_occupants,
            full_name=full_name,
            phone_number=phone_number,
            message=message,
            status='new',
            created_by=request.user
        )
        
        return JsonResponse({'success': True})
    
    except Exception as e:
        print('Error:', e)
        
        return JsonResponse({'success': False})
    
@api_view(['POST'])
def toggle_favourite(request, pk):
    property = Property.objects.get(pk=pk)
    
    if request.user in property.favourite.all():
        property.favourite.remove(request.user)
        
        return JsonResponse({'Is_favourite': False})
    
    else:
        property.favourite.add(request.user)
        
        return JsonResponse({'Is_favourite': True})