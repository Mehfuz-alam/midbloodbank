from django.urls import path

from django.contrib.auth.views import LoginView
from . import views
urlpatterns = [
    path('donorlogin', LoginView.as_view(template_name='donor/donorlogin.html'),name='donorlogin'),
    path('donorsignup', views.donor_signup_view,name='donorsignup'),
    path('donor-dashboard', views.donor_dashboard_view,name='donor-dashboard'),
    path('donate-blood', views.donate_blood_view,name='donate-blood'),
    path('donation-history', views.donation_history_view,name='donation-history'),
    path('make-request', views.make_request_view,name='make-request'),
    path('request-history', views.request_history_view,name='request-history'),
    path('verify-donor-email', views.verify_donor_email_view, name='verify-donor-email'),
    path('donor-password-reset', views.donor_password_reset_view, name='donor-password-reset'),
    path('confirm-donor-reset-otp', views.confirm_donor_reset_otp_view, name='confirm-donor-reset-otp'),
    path('set-donor-new-password', views.set_donor_new_password_view, name='set-donor-new-password'),
    path('nearby-donors/', views.nearby_donors, name='nearby_donors'),
    path('track-location/', views.track_donor_location, name='track-donor-location'),
    path('get-location/', views.get_donor_location, name='get-donor-location'),
    path('donor-profile/', views.donor_profile_view, name='donor-profile'),
    path('edit-donor-profile/', views.edit_donor_profile_view, name='edit-patient-profile'),
]
