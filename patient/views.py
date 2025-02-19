import random
from django.shortcuts import render, redirect, reverse
from . import forms, models
from django.db.models import Sum, Q
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from datetime import date, timedelta
from django.core.mail import send_mail
from django.contrib.auth.models import User
from blood import forms as bforms
from blood import models as bmodels

# Generate a random OTP
def generate_otp():
    return random.randint(100000, 999999)

def patient_signup_view(request):
    userForm = forms.PatientUserForm()
    patientForm = forms.PatientForm()
    mydict = {'userForm': userForm, 'patientForm': patientForm}

    if request.method == 'POST':
        userForm = forms.PatientUserForm(request.POST)
        patientForm = forms.PatientForm(request.POST, request.FILES)
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        if userForm.is_valid() and patientForm.is_valid():
            user = userForm.save(commit=False)
            user.set_password(user.password)
            user.is_active = False  # Make user inactive until email verification
            user.save()

            patient = patientForm.save(commit=False)
            patient.user = user
            patient.bloodgroup = patientForm.cleaned_data['bloodgroup']
            patient.latitude = latitude
            patient.longitude = longitude
            patient.save()

            my_patient_group = Group.objects.get_or_create(name='PATIENT')
            my_patient_group[0].user_set.add(user)

            # Generate OTP
            otp = generate_otp()
            request.session['otp'] = otp
            request.session['email'] = user.email

            # Send email with OTP
            send_mail(
                'Verify Your Email',
                f'Congratulations! You have signed up successfully.\n\nYour OTP for email verification is: {otp}',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            return redirect('verify-email')
    return render(request, 'patient/patientsignup.html', context=mydict)

def verify_email_view(request):
    if request.method == 'POST':
        otp_entered = request.POST.get('otp')
        otp_session = request.session.get('otp')
        email = request.session.get('email')

        if otp_entered and otp_session and int(otp_entered) == otp_session:
            user = User.objects.get(email=email)
            user.is_active = True
            user.save()

            # Clear session data
            del request.session['otp']
            del request.session['email']

            return redirect('patientlogin')
        else:
            return render(request, 'patient/verify_email.html', {'error': 'Invalid OTP. Please try again.'})
    return render(request, 'patient/verify_email.html')

def patient_dashboard_view(request):
    patient = models.Patient.objects.get(user_id=request.user.id)
    dict = {
        'requestpending': bmodels.BloodRequest.objects.all().filter(request_by_patient=patient).filter(status='Pending').count(),
        'requestapproved': bmodels.BloodRequest.objects.all().filter(request_by_patient=patient).filter(status='Approved').count(),
        'requestmade': bmodels.BloodRequest.objects.all().filter(request_by_patient=patient).count(),
        'requestrejected': bmodels.BloodRequest.objects.all().filter(request_by_patient=patient).filter(status='Rejected').count(),
    }
    return render(request, 'patient/patient_dashboard.html', context=dict)

def make_request_view(request):
    request_form = bforms.RequestForm()
    if request.method == 'POST':
        request_form = bforms.RequestForm(request.POST)
        if request_form.is_valid():
            blood_request = request_form.save(commit=False)
            blood_request.bloodgroup = request_form.cleaned_data['bloodgroup']
            patient = models.Patient.objects.get(user_id=request.user.id)
            blood_request.request_by_patient = patient
            blood_request.save()
            return HttpResponseRedirect('my-request')  
    return render(request, 'patient/makerequest.html', {'request_form': request_form})

def my_request_view(request):
    patient = models.Patient.objects.get(user_id=request.user.id)
    blood_request = bmodels.BloodRequest.objects.all().filter(request_by_patient=patient)
    return render(request, 'patient/my_request.html', {'blood_request': blood_request})

def password_reset_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            otp = generate_otp()
            request.session['reset_otp'] = otp
            request.session['reset_email'] = email

            # Send reset email
            send_mail(
                'Password Reset Request',
                f'Your OTP for resetting your password is: {otp}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            return redirect('confirm-reset-otp')
        except User.DoesNotExist:
            return render(request, 'patient/password_reset.html', {'error': 'Email not found.'})
    return render(request, 'patient/password_reset.html')

def confirm_reset_otp_view(request):
    if request.method == 'POST':
        otp_entered = request.POST.get('otp')
        otp_session = request.session.get('reset_otp')
        email = request.session.get('reset_email')

        if otp_entered and otp_session and int(otp_entered) == otp_session:
            return redirect('set-new-password')
        else:
            return render(request, 'patient/confirm_reset_otp.html', {'error': 'Invalid OTP. Please try again.'})
    return render(request, 'patient/confirm_reset_otp.html')

def set_new_password_view(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        email = request.session.get('reset_email')
        user = User.objects.get(email=email)
        user.set_password(password)
        user.save()

        # Clear session data
        del request.session['reset_otp']
        del request.session['reset_email']

        return redirect('patientlogin')
    return render(request, 'patient/set_new_password.html')






from django.contrib import messages

@login_required
def patient_profile_view(request):
    try:
        patient = models.Patient.objects.get(user=request.user)
        return render(request, 'patient/patient_profile.html', {'patient': patient})
    except models.Patient.DoesNotExist:
        messages.error(request, "Patient profile not found.")
        return redirect('patient-dashboard')
    

# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from . import models, forms

# @login_required
# def edit_patient_profile_view(request):
#     patient = models.Patient.objects.get(user=request.user)
#     user = request.user

#     if request.method == 'POST':
#         user_form = forms.PatientUserForm(request.POST, instance=user)
#         patient_form = forms.PatientForm(request.POST, request.FILES, instance=patient)

#         if user_form.is_valid() and patient_form.is_valid():
#             user_form.save()  # Directly save user form (no need for manual field updates)
#             patient_form.save()

#             messages.success(request, "Profile updated successfully!")
#             return redirect('patient-profile')
#         else:
#             messages.error(request, "Please correct the errors below.")
#     else:
#         user_form = forms.PatientUserForm(instance=user)
#         patient_form = forms.PatientForm(instance=patient)

#     return render(request, 'patient/edit_patient_profile.html', {
#         'user_form': user_form,
#         'patient_form': patient_form,
#     })
