from django.http import JsonResponse
from django.db.models import Q

from rest_framework.decorators import api_view,authentication_classes,permission_classes
from .models import Property, Reservation, VideoCallSchedule
from .serializers import PropertyListSerializer, PropertiesDetailSerializer, VideoCallScheduleSerializer
from .forms import PropertyForm
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.permissions import IsAuthenticated
from users.models import User
import uuid
from datetime import datetime


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
    
    #Filters
    
    is_favourites = request.GET.get('is_favourites', '')
    landlord_id = request.GET.get('landlord_id', None)
    
    district = request.GET.get('district', '')
    category = request.GET.get('selectedCategory', '')
    budget = request.GET.get('budgetRange', '')
    rooms = request.GET.get('numRooms','')
    kitchen = request.GET.get('numKitchen', '')
    bathrooms = request.GET.get('numBathrooms', '')
    
    if landlord_id:
        properties = Property.objects.filter(landlord_id=landlord_id)
    else:
        properties = Property.objects.all()
        
    if is_favourites:
        properties = properties.filter(favourite__in=[user])
        
    if district:
        properties = properties.filter(district=district)
        
    if category and category != 'undefined':
        category_map = {
            'single_room': ['Single Room', 'SingleRooms'],
            'flat': ['Flats'],
            'office': ['OfficeSpace'],
            'warehouse': ['Warehouse']
        }
        db_categories = category_map.get(category, [category])
        properties = properties.filter(category__in=db_categories)
    
    if budget:
        try:
            # budget comes as "[5000, 25000]" from frontend
            budget = budget.strip('[]').split(',')
            min_budget = int(budget[0])
            max_budget = int(budget[1])
            properties = properties.filter(
                price_per_month__gte=min_budget,
                price_per_month__lte=max_budget
            )
        except:
            pass
    
    if rooms:
        properties = properties.filter(rooms__gte=rooms)
        
    if kitchen:
        properties = properties.filter(kitchen__gte=kitchen)
        
    if bathrooms:
        properties = properties.filter(bathrooms__gte=bathrooms)
        
        
        
    
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

@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_property(request, pk):
    try:
        property = Property.objects.get(pk=pk)
        
        # Only allow owner to delete
        if property.landlord != request.user:
            return JsonResponse({'success': False, 'error': 'Not authorized'}, status=403)
        
        property.delete()
        return JsonResponse({'success': True})
    except Property.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Property not found'}, status=404)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def toggle_availability(request, pk):
    try:
        property = Property.objects.get(pk=pk)
        
        # Only allow owner to toggle
        if property.landlord != request.user:
            return JsonResponse({'success': False, 'error': 'Not authorized'}, status=403)
        
        property.is_available = not property.is_available
        property.save()
        return JsonResponse({'success': True, 'is_available': property.is_available})
    except Property.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Property not found'}, status=404)
    
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
        
        # Prevent owner from booking their own property
        if property.landlord == request.user:
            return JsonResponse({'success': False, 'error': 'You cannot inquire about your own property'}, status=400)
        
        reservation = Reservation.objects.create(
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
        
        # Send notification to owner via WebSocket
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'notifications_{property.landlord.id}',
                {
                    'type': 'send_notification',
                    'message': f'New inquiry for "{property.title}" from {full_name}',
                    'notification_type': 'inquiry',
                    'url': '/myinquiries'
                }
            )
        except Exception as e:
            print(f'Error sending notification: {e}')
        
        return JsonResponse({'success': True})
    
    except Exception as e:
        print('Error:', e)
        
        return JsonResponse({'success': False})

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_my_inquiries(request):
    """Get all inquiries/reservations for the landlord's properties"""
    from .serializers import ReservationsListSerializer
    
    # Get all properties owned by this user
    my_properties = Property.objects.filter(landlord=request.user)
    
    # Get all reservations for those properties
    inquiries = Reservation.objects.filter(property__in=my_properties).order_by('-created_at')
    
    serializer = ReservationsListSerializer(inquiries, many=True)
    return JsonResponse({'data': serializer.data})
    
@api_view(['POST'])
def toggle_favourite(request, pk):
    property = Property.objects.get(pk=pk)
    
    if request.user in property.favourite.all():
        property.favourite.remove(request.user)
        
        return JsonResponse({'Is_favourite': False})
    
    else:
        property.favourite.add(request.user)
        
        return JsonResponse({'Is_favourite': True})


# Video Call APIs
@api_view(['POST'])
def schedule_video_call(request, pk):
    """Schedule a video call for a property"""
    try:
        # Get token from header
        token = request.META.get('HTTP_AUTHORIZATION', '').split('Bearer ')[1]
        token = AccessToken(token)
        user_id = token.payload['user_id']
        user = User.objects.get(pk=user_id)
        
        property = Property.objects.get(pk=pk)
        scheduled_time = request.data.get('scheduled_time')
        
        # Generate unique room name
        room_name = f"roomsmandu-{property.id}-{uuid.uuid4().hex[:8]}"
        
        # Create video call schedule
        video_call = VideoCallSchedule.objects.create(
            property=property,
            tenant=user,
            landlord=property.landlord,
            scheduled_time=scheduled_time,
            room_name=room_name,
            status='pending'
        )
        
        # Send notification to landlord
        from chat.utils import send_notification
        send_notification(
            property.landlord.id, 
            f"📞 New video call request for '{property.title}'",
            'call'
        )
        
        serializer = VideoCallScheduleSerializer(video_call)
        return JsonResponse({'success': True, 'data': serializer.data})
    
    except Exception as e:
        import traceback
        print('Error scheduling video call:', str(e))
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@api_view(['GET'])
def get_my_video_calls(request):
    """Get all video calls for current user (as tenant or landlord)"""
    try:
        token = request.META.get('HTTP_AUTHORIZATION', '').split('Bearer ')[1]
        token = AccessToken(token)
        user_id = token.payload['user_id']
        user = User.objects.get(pk=user_id)
        
        calls = VideoCallSchedule.objects.filter(
            Q(tenant=user) | Q(landlord=user)
        ).order_by('-scheduled_time')
        
        serializer = VideoCallScheduleSerializer(calls, many=True)
        return JsonResponse(serializer.data, safe=False)
    
    except Exception as e:
        return JsonResponse([], safe=False)


@api_view(['GET'])
def get_video_call(request, pk):
    """Get a single video call by ID"""
    try:
        # Get token from header
        token = request.META.get('HTTP_AUTHORIZATION', '').split('Bearer ')[1]
        token = AccessToken(token)
        user_id = token.payload['user_id']
        user = User.objects.get(pk=user_id)
        
        video_call = VideoCallSchedule.objects.get(pk=pk)
        
        # Only tenant or landlord can view
        if user != video_call.tenant and user != video_call.landlord:
            return JsonResponse({'error': 'Not authorized'}, status=403)
        
        serializer = VideoCallScheduleSerializer(video_call, many=False)
        return JsonResponse(serializer.data)
    
    except VideoCallSchedule.DoesNotExist:
        return JsonResponse({'error': 'Video call not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@api_view(['POST'])
def confirm_video_call(request, pk):
    """Landlord confirms a video call"""
    try:
        # Get token from header
        token = request.META.get('HTTP_AUTHORIZATION', '').split('Bearer ')[1]
        token = AccessToken(token)
        user_id = token.payload['user_id']
        user = User.objects.get(pk=user_id)
        
        video_call = VideoCallSchedule.objects.get(pk=pk)
        
        # Only landlord can confirm
        if user != video_call.landlord:
            return JsonResponse({'success': False, 'error': 'Only landlord can confirm'}, status=403)
        
        video_call.status = 'confirmed'
        video_call.save()
        
        # Send notification to tenant
        from chat.utils import send_notification
        send_notification(
            video_call.tenant.id, 
            f"✅ Your video call for '{video_call.property.title}' has been confirmed!",
            'success'
        )
        
        serializer = VideoCallScheduleSerializer(video_call, many=False)
        return JsonResponse({'success': True, 'data': serializer.data})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)