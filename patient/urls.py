from django.urls import path
from django.contrib.auth.views import LoginView
from . import views

urlpatterns = [
    path('patientlogin', LoginView.as_view(template_name='patient/patientlogin.html'), name='patientlogin'),
    path('patientsignup', views.patient_signup_view, name='patientsignup'),
    path('verify-email', views.verify_email_view, name='verify-email'),
    path('patient-dashboard', views.patient_dashboard_view, name='patient-dashboard'),
    path('make-request', views.make_request_view, name='make-request'),
    path('my-request', views.my_request_view, name='my-request'),
    path('password-reset', views.password_reset_view, name='password-reset'),
    path('confirm-reset-otp', views.confirm_reset_otp_view, name='confirm-reset-otp'),
    path('set-new-password', views.set_new_password_view, name='set-new-password'),
]
