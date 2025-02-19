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
from donor import models as dmodels
from patient import models as pmodels
from donor import forms as dforms
from patient import forms as pforms

def home_view(request):
    x=models.Stock.objects.all()
    print(x)
    if len(x)==0:
        blood1=models.Stock()
        blood1.bloodgroup="A+"
        blood1.save()

        blood2=models.Stock()
        blood2.bloodgroup="A-"
        blood2.save()

        blood3=models.Stock()
        blood3.bloodgroup="B+"
        blood3.save()        

        blood4=models.Stock()
        blood4.bloodgroup="B-"
        blood4.save()

        blood5=models.Stock()
        blood5.bloodgroup="AB+"
        blood5.save()

        blood6=models.Stock()
        blood6.bloodgroup="AB-"
        blood6.save()

        blood7=models.Stock()
        blood7.bloodgroup="O+"
        blood7.save()

        blood8=models.Stock()
        blood8.bloodgroup="O-"
        blood8.save()

    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')  
    return render(request,'blood/index.html')

def is_donor(user):
    return user.groups.filter(name='DONOR').exists()

def is_patient(user):
    return user.groups.filter(name='PATIENT').exists()


def afterlogin_view(request):
    if is_donor(request.user):      
        return redirect('donor/donor-dashboard')
                
    elif is_patient(request.user):
        return redirect('patient/patient-dashboard')
    else:
        return redirect('admin-dashboard')

@login_required(login_url='adminlogin')
def admin_dashboard_view(request):
    totalunit = models.Stock.objects.aggregate(Sum('unit'))
    chart1, chart2 = generate_blood_charts()  # Generate the charts

    dict = {
        'A1': models.Stock.objects.get(bloodgroup="A+"),
        'A2': models.Stock.objects.get(bloodgroup="A-"),
        'B1': models.Stock.objects.get(bloodgroup="B+"),
        'B2': models.Stock.objects.get(bloodgroup="B-"),
        'AB1': models.Stock.objects.get(bloodgroup="AB+"),
        'AB2': models.Stock.objects.get(bloodgroup="AB-"),
        'O1': models.Stock.objects.get(bloodgroup="O+"),
        'O2': models.Stock.objects.get(bloodgroup="O-"),
        'totaldonors': dmodels.Donor.objects.all().count(),
        'totalbloodunit': totalunit['unit__sum'],
        'totalrequest': models.BloodRequest.objects.all().count(),
        'totalapprovedrequest': models.BloodRequest.objects.all().filter(status='Approved').count(),
        'chart1': chart1,  # Add chart1 to the context
        'chart2': chart2,  # Add chart2 to the context
    }
    return render(request, 'blood/admin_dashboard.html', context=dict)

# @login_required(login_url='adminlogin')
# def admin_blood_view(request):
#     dict={
#         'bloodForm':forms.BloodForm(),
#         'A1':models.Stock.objects.get(bloodgroup="A+"),
#         'A2':models.Stock.objects.get(bloodgroup="A-"),
#         'B1':models.Stock.objects.get(bloodgroup="B+"),
#         'B2':models.Stock.objects.get(bloodgroup="B-"),
#         'AB1':models.Stock.objects.get(bloodgroup="AB+"),
#         'AB2':models.Stock.objects.get(bloodgroup="AB-"),
#         'O1':models.Stock.objects.get(bloodgroup="O+"),
#         'O2':models.Stock.objects.get(bloodgroup="O-"),
#     }
#     if request.method=='POST':
#         bloodForm=forms.BloodForm(request.POST)
#         if bloodForm.is_valid() :        
#             bloodgroup=bloodForm.cleaned_data['bloodgroup']
#             stock=models.Stock.objects.get(bloodgroup=bloodgroup)
#             stock.unit=bloodForm.cleaned_data['unit']
#             stock.save()
#         return HttpResponseRedirect('admin-blood')
#     return render(request,'blood/admin_blood.html',context=dict)

# views.py
from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from . import forms, models

@login_required(login_url='adminlogin')
@login_required(login_url='adminlogin')
def admin_blood_view(request):
    # Fetching blood stock data
    blood_stock = {
        'A1': models.Stock.objects.get(bloodgroup="A+"),
        'A2': models.Stock.objects.get(bloodgroup="A-"),
        'B1': models.Stock.objects.get(bloodgroup="B+"),
        'B2': models.Stock.objects.get(bloodgroup="B-"),
        'AB1': models.Stock.objects.get(bloodgroup="AB+"),
        'AB2': models.Stock.objects.get(bloodgroup="AB-"),
        'O1': models.Stock.objects.get(bloodgroup="O+"),
        'O2': models.Stock.objects.get(bloodgroup="O-"),
    }
    total_blood_stock = sum(stock.unit for stock in blood_stock.values())
    # Fetching blood request data by type and month
    blood_requests = models.BloodRequest.objects.all()
    request_data = {}

    for req in blood_requests:
        month = req.date.month
        blood_type = req.bloodgroup
        if month not in request_data:
            request_data[month] = {}
        if blood_type not in request_data[month]:
            request_data[month][blood_type] = 0
        request_data[month][blood_type] += req.unit

    # Prepare data for the chart
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    blood_types = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    chart_data = {bt: [request_data.get(m, {}).get(bt, 0) for m in range(1, 13)] for bt in blood_types}

    # Pre-calculate colors for each blood type
    colors = []
    for i in range(len(blood_types)):
        r = i * 30  # Calculate the red component
        colors.append({
            'background': f'rgba({r}, 99, 132, 0.2)',
            'border': f'rgba({r}, 99, 132, 1)',
        })

    context = {
        'bloodForm': forms.BloodForm(),
        **blood_stock,
        'total_blood_stock': total_blood_stock,
        'chart_data': chart_data,
        'months': months,
        'blood_types': blood_types,
        'colors': colors,  # Pass pre-calculated colors to the template
    }

    if request.method == 'POST':
        bloodForm = forms.BloodForm(request.POST)
        if bloodForm.is_valid():
            bloodgroup = bloodForm.cleaned_data['bloodgroup']
            stock = models.Stock.objects.get(bloodgroup=bloodgroup)
            stock.unit = bloodForm.cleaned_data['unit']
            stock.save()
            return HttpResponseRedirect('admin-blood')
    return render(request, 'blood/admin_blood.html', context=context)


@login_required(login_url='adminlogin')
def admin_donor_view(request):
    donors=dmodels.Donor.objects.all()
    return render(request,'blood/admin_donor.html',{'donors':donors})

@login_required(login_url='adminlogin')
def update_donor_view(request,pk):
    donor=dmodels.Donor.objects.get(id=pk)
    user=dmodels.User.objects.get(id=donor.user_id)
    userForm=dforms.DonorUserForm(instance=user)
    donorForm=dforms.DonorForm(request.FILES,instance=donor)
    mydict={'userForm':userForm,'donorForm':donorForm}
    if request.method=='POST':
        userForm=dforms.DonorUserForm(request.POST,instance=user)
        donorForm=dforms.DonorForm(request.POST,request.FILES,instance=donor)
        if userForm.is_valid() and donorForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            donor=donorForm.save(commit=False)
            donor.user=user
            donor.bloodgroup=donorForm.cleaned_data['bloodgroup']
            donor.save()
            return redirect('admin-donor')
    return render(request,'blood/update_donor.html',context=mydict)


@login_required(login_url='adminlogin')
def delete_donor_view(request,pk):
    donor=dmodels.Donor.objects.get(id=pk)
    user=User.objects.get(id=donor.user_id)
    user.delete()
    donor.delete()
    return HttpResponseRedirect('/admin-donor')

@login_required(login_url='adminlogin')
def admin_patient_view(request):
    patients=pmodels.Patient.objects.all()
    return render(request,'blood/admin_patient.html',{'patients':patients})


@login_required(login_url='adminlogin')
def update_patient_view(request,pk):
    patient=pmodels.Patient.objects.get(id=pk)
    user=pmodels.User.objects.get(id=patient.user_id)
    userForm=pforms.PatientUserForm(instance=user)
    patientForm=pforms.PatientForm(request.FILES,instance=patient)
    mydict={'userForm':userForm,'patientForm':patientForm}
    if request.method=='POST':
        userForm=pforms.PatientUserForm(request.POST,instance=user)
        patientForm=pforms.PatientForm(request.POST,request.FILES,instance=patient)
        if userForm.is_valid() and patientForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            patient=patientForm.save(commit=False)
            patient.user=user
            patient.bloodgroup=patientForm.cleaned_data['bloodgroup']
            patient.save()
            return redirect('admin-patient')
    return render(request,'blood/update_patient.html',context=mydict)

# @login_required(login_url='adminlogin')
# def update_patient_view(request, pk):
#     patient = pmodels.Patient.objects.get(id=pk)
#     user = patient.user
#     userForm = pforms.PatientUserForm(instance=user)
#     patientForm = pforms.PatientForm(request.FILES, instance=patient)
#     mydict = {'userForm': userForm, 'patientForm': patientForm}

#     if request.method == 'POST':
#         userForm = pforms.PatientUserForm(request.POST, instance=user)
#         patientForm = pforms.PatientForm(request.POST, request.FILES, instance=patient)
#         if userForm.is_valid() and patientForm.is_valid():
#             user = userForm.save()  # Password is handled in the form's save method
#             patient = patientForm.save(commit=False)
#             patient.user = user
#             patient.bloodgroup = patientForm.cleaned_data['bloodgroup']
#             patient.save()
#             return redirect('admin-patient')
#         else:
#             # Print form errors to debug
#             print("User Form Errors:", userForm.errors)
#             print("Patient Form Errors:", patientForm.errors)
#     return render(request, 'blood/update_patient.html', context=mydict)


@login_required(login_url='adminlogin')
def delete_patient_view(request,pk):
    patient=pmodels.Patient.objects.get(id=pk)
    user=User.objects.get(id=patient.user_id)
    user.delete()
    patient.delete()
    return HttpResponseRedirect('/admin-patient')

@login_required(login_url='adminlogin')
def admin_request_view(request):
    requests=models.BloodRequest.objects.all().filter(status='Pending')
    return render(request,'blood/admin_request.html',{'requests':requests})

@login_required(login_url='adminlogin')
def admin_request_history_view(request):
    requests=models.BloodRequest.objects.all().exclude(status='Pending')
    return render(request,'blood/admin_request_history.html',{'requests':requests})

@login_required(login_url='adminlogin')
def admin_donation_view(request):
    donations=dmodels.BloodDonate.objects.all()
    return render(request,'blood/admin_donation.html',{'donations':donations})

@login_required(login_url='adminlogin')
def update_approve_status_view(request,pk):
    req=models.BloodRequest.objects.get(id=pk)
    message=None
    bloodgroup=req.bloodgroup
    unit=req.unit
    stock=models.Stock.objects.get(bloodgroup=bloodgroup)
    if stock.unit > unit:
        stock.unit=stock.unit-unit
        stock.save()
        req.status="Approved"
        
    else:
        message="Stock Doest Not Have Enough Blood To Approve This Request, Only "+str(stock.unit)+" Unit Available"
    req.save()

    requests=models.BloodRequest.objects.all().filter(status='Pending')
    return render(request,'blood/admin_request.html',{'requests':requests,'message':message})

@login_required(login_url='adminlogin')
def update_reject_status_view(request,pk):
    req=models.BloodRequest.objects.get(id=pk)
    req.status="Rejected"
    req.save()
    return HttpResponseRedirect('/admin-request')

@login_required(login_url='adminlogin')
def approve_donation_view(request,pk):
    donation=dmodels.BloodDonate.objects.get(id=pk)
    donation_blood_group=donation.bloodgroup
    donation_blood_unit=donation.unit

    stock=models.Stock.objects.get(bloodgroup=donation_blood_group)
    stock.unit=stock.unit+donation_blood_unit
    stock.save()

    donation.status='Approved'
    donation.save()
    return HttpResponseRedirect('/admin-donation')


@login_required(login_url='adminlogin')
def reject_donation_view(request,pk):
    donation=dmodels.BloodDonate.objects.get(id=pk)
    donation.status='Rejected'
    donation.save()
    return HttpResponseRedirect('/admin-donation')

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # This prevents GUI-related errors in Django

import numpy as np
import io
import base64
from django.shortcuts import render
from .models import Stock, BloodRequest  # Import from blood.models
from donor.models import BloodDonate  # Import from donor.models

from datetime import datetime, timedelta

def generate_blood_charts():
    # Get the current year and month
    now = datetime.now()
    current_year = now.year

    # Initialize data structures
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    donations = [0] * 12
    requests = [0] * 12

    # Query donations and requests for the current year
    for i in range(1, 13):
        start_date = datetime(current_year, i, 1)
        if i == 12:
            end_date = datetime(current_year + 1, 1, 1)
        else:
            end_date = datetime(current_year, i + 1, 1)

        # Count donations and requests for each month
        donations[i - 1] = BloodDonate.objects.filter(date__gte=start_date, date__lt=end_date).count()
        requests[i - 1] = BloodRequest.objects.filter(date__gte=start_date, date__lt=end_date).count()

    # Create the figure for donations vs requests
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(months, donations, marker='o', linestyle='-', color='blue', label='Monthly Donations')
    ax.plot(months, requests, marker='o', linestyle='-', color='red', label='Monthly Requests')
    ax.set_title("Monthly Donations vs Requests")
    ax.set_xlabel("Months")
    ax.set_ylabel("Units of Blood")
    ax.legend()
    ax.grid()

    # Convert to base64 image
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    chart1 = base64.b64encode(buffer.getvalue()).decode()
    buffer.close()

    # Blood Stock Levels Over Months
    blood_groups = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
    stock_levels = []

    # Query stock levels for each blood group
    for bg in blood_groups:
        stock = Stock.objects.filter(bloodgroup=bg).first()
        if stock:
            stock_levels.append(stock.unit)
        else:
            stock_levels.append(0)

    # Create the figure for blood stock levels
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(blood_groups, stock_levels, color='green')
    ax.set_title("Blood Stock Levels")
    ax.set_xlabel("Blood Groups")
    ax.set_ylabel("Stock Levels (Units)")
    ax.grid()

    # Convert to base64 image
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    chart2 = base64.b64encode(buffer.getvalue()).decode()
    buffer.close()

    return chart1, chart2

def blood_analytics(request):
    chart1, chart2 = generate_blood_charts()
    return render(request, 'admin_dashboard.html', {'chart1': chart1, 'chart2': chart2})



from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views import View

class CustomLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('home')  # Redirect to the home page after logout

    def post(self, request):
        logout(request)
        return redirect('home')  # Redirect to the home page after logout