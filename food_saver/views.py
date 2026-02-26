from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .models import User, FoodDonation, Pickup
from django.contrib import messages
from .utils import predict_expiry, calculate_distance
from django.utils import timezone
import json

def index(request):
    return render(request, 'food_saver/index.html')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        phone = request.POST.get('phone', '')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'food_saver/register.html')
            
        user = User.objects.create_user(username=username, email=email, password=password, role=role, phone=phone)
        login(request, user)
        messages.success(request, f'Registration successful as {role.upper()}')
        return redirect('dashboard')
    return render(request, 'food_saver/register.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'food_saver/login.html')

def user_logout(request):
    logout(request)
    return redirect('index')

@login_required
def dashboard(request):
    params = request.GET
    lat = params.get('lat')
    lng = params.get('lng')

    # Update user location if provided (simulating GPS update)
    if lat and lng:
        request.user.location_lat = float(lat)
        request.user.location_lng = float(lng)
        request.user.save()

    # Dynamic Statistics
    stats = {
        'total_saved': FoodDonation.objects.count(),
        'meals_served': FoodDonation.objects.count() * 10, # Mock: 1 donation = 10 meals
    }

    context = {
        'donations': FoodDonation.objects.all().order_by('-created_at'),
        'stats': stats,
    }

    if request.user.role == 'donor':
        context['my_donations'] = FoodDonation.objects.filter(donor=request.user)
    elif request.user.role == 'ngo':
        # Smart Matching: Show nearby pending donations within 10km
        available = FoodDonation.objects.filter(status='pending')
        nearby_donations = []
        
        if request.user.location_lat and request.user.location_lng:
            for donation in available:
                dist = calculate_distance(
                    request.user.location_lat, request.user.location_lng,
                    donation.location_lat, donation.location_lng
                )
                if dist <= 10: # 10km radius
                    donation.distance = round(dist, 1)
                    nearby_donations.append(donation)
            context['available_donations'] = nearby_donations
        else:
            context['available_donations'] = available
            
    elif request.user.role == 'volunteer':
        # Volunteers see donations accepted by NGOs that need a volunteer
        context['available_tasks'] = FoodDonation.objects.filter(status='accepted', pickup__volunteer__isnull=True)
        my_tasks = Pickup.objects.filter(volunteer=request.user)
        context['my_tasks'] = my_tasks
        
        # Pull donor locations for active missions
        mission_locations = []
        for task in my_tasks:
            mission_locations.append({
                'name': task.donation.name,
                'lat': task.donation.location_lat,
                'lng': task.donation.location_lng,
                'status': task.donation.status
            })
        context['mission_locations'] = mission_locations
    
    return render(request, 'food_saver/dashboard.html', context)

@login_required
def upload_food(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        food_type = request.POST.get('food_type')
        quantity = request.POST.get('quantity')
        lat = float(request.POST.get('lat', 0))
        lng = float(request.POST.get('lng', 0))
        address = request.POST.get('address', '')
        instructions = request.POST.get('special_instructions', '')
        
        image = request.FILES.get('image')
        
        # AI-based Expiry Prediction logic
        prep_time = timezone.now()
        expiry_time = predict_expiry(food_type, prep_time)
        
        donation = FoodDonation.objects.create(
            donor=request.user,
            name=name,
            food_type=food_type,
            quantity=quantity,
            preparation_time=prep_time,
            expiry_time=expiry_time,
            location_lat=lat,
            location_lng=lng,
            address=address,
            special_instructions=instructions,
            image=image
        )
        
        messages.success(request, f'Food "{name}" uploaded! AI predicted expiry: {expiry_time.strftime("%H:%M")}')
        return redirect('dashboard')
    return redirect('dashboard')

@login_required
def claim_donation(request, donation_id):
    if request.user.role == 'ngo':
        donation = FoodDonation.objects.get(id=donation_id)
        if donation.status == 'pending':
            donation.status = 'accepted'
            donation.save()
            Pickup.objects.create(donation=donation, ngo=request.user)
            messages.success(request, f'You have claimed "{donation.name}" for pickup!')
    return redirect('dashboard')

@login_required
def volunteer_accept_task(request, donation_id):
    if request.user.role == 'volunteer':
        pickup = Pickup.objects.get(donation_id=donation_id)
        if not pickup.volunteer:
            pickup.volunteer = request.user
            pickup.save()
            messages.success(request, f'You have accepted the pickup task for "{pickup.donation.name}"')
    return redirect('dashboard')

@login_required
def volunteer_confirm_pickup(request, pickup_id):
    if request.user.role == 'volunteer':
        pickup = Pickup.objects.get(id=pickup_id)
        if pickup.volunteer == request.user:
            pickup.picked_up_at = timezone.now()
            pickup.save()
            donation = pickup.donation
            donation.status = 'picked_up'
            donation.save()
            messages.success(request, f'Pickup confirmed for "{donation.name}"')
    return redirect('dashboard')

@login_required
def volunteer_confirm_delivery(request, pickup_id):
    if request.user.role == 'volunteer':
        pickup = Pickup.objects.get(id=pickup_id)
        if pickup.volunteer == request.user:
            pickup.delivered_at = timezone.now()
            pickup.save()
            donation = pickup.donation
            donation.status = 'delivered'
            donation.save()
            
            # Increment reward points
            request.user.reward_points += 10
            request.user.save()
            
            messages.success(request, f'Delivery confirmed for "{donation.name}"! You earned 10 Reward Points! 🏆')
    return redirect('dashboard')

@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        return redirect('dashboard')
    
    context = {
        'total_users': User.objects.count(),
        'total_donations': FoodDonation.objects.count(),
        'total_delivered': FoodDonation.objects.filter(status='delivered').count(),
        'recent_donations': FoodDonation.objects.all().order_by('-created_at')[:10],
        'all_users': User.objects.all().order_by('-date_joined')[:20],
    }
    return render(request, 'food_saver/admin_dashboard.html', context)

@login_required
def toggle_fraud(request, user_id):
    if request.user.role == 'admin':
        if request.method == 'POST':
            target_user = get_object_or_404(User, id=user_id)
            if target_user != request.user:
                target_user.is_fraudulent = not target_user.is_fraudulent
                target_user.save()
                status = "flagged as fraud" if target_user.is_fraudulent else "unflagged"
                messages.success(request, f'User {target_user.username} has been {status}.')
    return redirect('admin_dashboard')

@login_required
def donation_detail(request, donation_id):
    donation = get_object_or_404(FoodDonation, id=donation_id)
    return render(request, 'food_saver/donation_detail.html', {'donation': donation})
