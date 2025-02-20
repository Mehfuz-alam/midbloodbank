from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum,Q
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from django.core.mail import send_mail
from django.contrib.auth.models import User
from blood import forms as bforms
from blood import models as bmodels

from django.shortcuts import render, redirect
from django.contrib.auth.models import Group, User
from django.core.mail import send_mail
from django.conf import settings
from . import forms
from .models import Donor, OTP
import random




# Utility function to generate OTP
def generate_otp():
    return random.randint(100000, 999999)

# Donor signup view
def donor_signup_view(request):
    userForm = forms.DonorUserForm()
    donorForm = forms.DonorForm()
    mydict = {'userForm': userForm, 'donorForm': donorForm}

    if request.method == 'POST':
        userForm = forms.DonorUserForm(request.POST)
        donorForm = forms.DonorForm(request.POST, request.FILES)
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        if userForm.is_valid() and donorForm.is_valid():
            user = userForm.save(commit=False)
            user.set_password(user.password)
            user.is_active = False  # Account is inactive until email is verified
            user.save()

            donor = donorForm.save(commit=False)
            donor.user = user
            donor.latitude = latitude
            donor.longitude = longitude
            donor.save()

            my_donor_group = Group.objects.get_or_create(name='DONOR')
            my_donor_group[0].user_set.add(user)

            otp = generate_otp()
            request.session['otp'] = otp
            request.session['email'] = user.email

            # Send OTP to the provided email
            send_mail(
                'Verify Your Email',
                f'Your OTP for email verification is: {otp}',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            return redirect('verify-donor-email')  # Redirect to OTP verification page
    return render(request, 'donor/donorsignup.html', context=mydict)

# Email verification view
def verify_donor_email_view(request):
    if request.method == 'POST':
        otp_entered = request.POST.get('otp')
        otp_session = request.session.get('otp')
        email = request.session.get('email')

        if otp_entered and otp_session and int(otp_entered) == otp_session:
            user = User.objects.get(email=email)
            user.is_active = True  # Activate the user account
            user.save()

            # Clean up session data
            del request.session['otp']
            del request.session['email']

            return redirect('donorlogin')
        else:
            return render(request, 'donor/verify_email.html', {'error': 'Invalid OTP. Please try again.'})
    return render(request, 'donor/verify_email.html')

# Password reset view
def donor_password_reset_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            otp = generate_otp()
            request.session['reset_otp'] = otp
            request.session['reset_email'] = email

            # Send OTP to email for password reset
            send_mail(
                'Password Reset Request',
                f'Your OTP for resetting your password is: {otp}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            return redirect('confirm-donor-reset-otp')
        except User.DoesNotExist:
            return render(request, 'donor/password_reset.html', {'error': 'Email not found.'})
    return render(request, 'donor/password_reset.html')

# Confirm OTP for password reset
def confirm_donor_reset_otp_view(request):
    if request.method == 'POST':
        otp_entered = request.POST.get('otp')
        otp_session = request.session.get('reset_otp')
        email = request.session.get('reset_email')

        if otp_entered and otp_session and int(otp_entered) == otp_session:
            return redirect('set-donor-new-password')
        else:
            return render(request, 'donor/confirm_reset_otp.html', {'error': 'Invalid OTP. Please try again.'})
    return render(request, 'donor/confirm_reset_otp.html')

# Set a new password
def set_donor_new_password_view(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        email = request.session.get('reset_email')
        user = User.objects.get(email=email)
        user.set_password(password)
        user.save()

        # Clean up session data
        del request.session['reset_otp']
        del request.session['reset_email']

        return redirect('donorlogin')
    return render(request, 'donor/set_new_password.html')

# Donor dashboard view
@login_required
def donor_dashboard_view(request):
    donor = models.Donor.objects.get(user_id=request.user.id)
    dict = {
        'requestpending': bmodels.BloodRequest.objects.all().filter(request_by_donor=donor).filter(status='Pending').count(),
        'requestapproved': bmodels.BloodRequest.objects.all().filter(request_by_donor=donor).filter(status='Approved').count(),
        'requestmade': bmodels.BloodRequest.objects.all().filter(request_by_donor=donor).count(),
        'requestrejected': bmodels.BloodRequest.objects.all().filter(request_by_donor=donor).filter(status='Rejected').count(),
    }
    return render(request, 'donor/donor_dashboard.html', context=dict)

# Donate blood view
@login_required
def donate_blood_view(request):
    donation_form = forms.DonationForm()
    if request.method == 'POST':
        donation_form = forms.DonationForm(request.POST)
        if donation_form.is_valid():
            blood_donate = donation_form.save(commit=False)
            donor = models.Donor.objects.get(user_id=request.user.id)
            blood_donate.donor = donor
            blood_donate.save()
            return HttpResponseRedirect('donation-history')  
    return render(request, 'donor/donate_blood.html', {'donation_form': donation_form})

# Donation history view
@login_required
def donation_history_view(request):
    donor = models.Donor.objects.get(user_id=request.user.id)
    donations = models.BloodDonate.objects.filter(donor=donor)
    return render(request, 'donor/donation_history.html', {'donations': donations})

# Make blood request view
@login_required
def make_request_view(request):
    request_form = bforms.RequestForm()
    if request.method == 'POST':
        request_form = bforms.RequestForm(request.POST)
        if request_form.is_valid():
            blood_request = request_form.save(commit=False)
            donor = models.Donor.objects.get(user_id=request.user.id)
            blood_request.request_by_donor = donor
            blood_request.save()
            return HttpResponseRedirect('request-history')  
    return render(request, 'donor/makerequest.html', {'request_form': request_form})

# Request history view
@login_required
def request_history_view(request):
    donor = models.Donor.objects.get(user_id=request.user.id)
    blood_request = bmodels.BloodRequest.objects.filter(request_by_donor=donor)
    return render(request, 'donor/request_history.html', {'blood_request': blood_request})


from django.shortcuts import render
from .models import Donor
from .utils import haversine

from django.shortcuts import render
from .models import Donor
import json

def nearby_donors(request):
    user_lat = request.GET.get('latitude')
    user_lon = request.GET.get('longitude')

    # Check if latitude and longitude are provided
    if not user_lat or not user_lon:
        return render(request, 'donor/nearby_donors.html', {
            'error': 'Please provide your location (latitude and longitude).'
        })

    try:
        user_lat = float(user_lat)
        user_lon = float(user_lon)
    except (TypeError, ValueError):
        return render(request, 'donor/nearby_donors.html', {
            'error': 'Invalid latitude or longitude values.'
        })

    nearby = []
    for donor in Donor.objects.exclude(latitude__isnull=True, longitude__isnull=True):
        distance = haversine(user_lat, user_lon, donor.latitude, donor.longitude)
        if distance < 10:  # Example: within 10 km
            nearby.append({
                'get_name': donor.get_name,
                'address': donor.address,
                'latitude': donor.latitude,
                'longitude': donor.longitude,
                'mobile': donor.mobile,
                'bloodgroup':donor.bloodgroup,
            })

    # Convert the list of donors to JSON for use in the template
    donors_json = json.dumps(nearby)

    return render(request, 'donor/nearby_donors.html', {
        'donors': nearby,
        'donors_json': donors_json,
        'user_lat': user_lat,
        'user_lon': user_lon,
    })
from django.shortcuts import render
from .models import Donor

# Donor live location tracking view
@login_required
def track_donor_location(request):
    try:
        # Get the donor based on logged-in user
        donor = Donor.objects.get(user=request.user)
        lat = donor.latitude
        lon = donor.longitude
    except Donor.DoesNotExist:
        lat, lon = 22.5726, 88.3639  # Default to Kolkata if no donor found

    context = {
        'latitude': lat,
        'longitude': lon,
    }

    return render(request, 'donor/track_donor_location.html', context)

from django.http import JsonResponse

# Endpoint to get current donor location
@login_required
def get_donor_location(request):
    try:
        donor = Donor.objects.get(user=request.user)
        return JsonResponse({
            'latitude': donor.latitude,
            'longitude': donor.longitude
        })
    except Donor.DoesNotExist:
        return JsonResponse({
            'latitude': 22.5726,  # Default to Kolkata
            'longitude': 88.3639
        })


from django.contrib import messages

@login_required
def donor_profile_view(request):
    try:
        donor = models.Donor.objects.get(user=request.user)
        return render(request, 'donor/donor_profile.html', {'donor': donor})
    except models.Donor.DoesNotExist:
        messages.error(request, "Donor profile not found.")
        return redirect('donor-dashboard')