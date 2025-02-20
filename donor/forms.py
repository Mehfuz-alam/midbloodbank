from django import forms
from django.contrib.auth.models import User
from . import models
from .models import Donor
from django.core.exceptions import ValidationError

class DonorUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), label="Password")
    
    latitude = forms.FloatField(widget=forms.HiddenInput(),required=False)
    longitude = forms.FloatField(widget=forms.HiddenInput(),required=False)
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password', 'email', 'latitude', 'longitude']
    def clean_email(self):
        """Ensure the email is unique."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) < 5:
            raise ValidationError("Username must be at least 5 characters long.")
        if User.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken. Please choose a different one.")
        return username
    
class DonorUserUpdateForm(forms.ModelForm):
    """Form for updating only first_name and last_name."""
    class Meta:
        model = User
        fields = ['first_name', 'last_name'] 


class DonorForm(forms.ModelForm):
  
    latitude = forms.FloatField(widget=forms.HiddenInput(),required=False)
    longitude = forms.FloatField(widget=forms.HiddenInput(),required=False)
    class Meta:
        model = Donor
        fields = ['bloodgroup','address', 'mobile', 'profile_pic','latitude', 'longitude']
    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        if len(mobile) != 10 or not mobile.isdigit():
            raise ValidationError("Phone number must be exactly 10 digits long.")
        return mobile

class OTPVerificationForm(forms.Form):
    otp = forms.CharField(label="Enter OTP", max_length=6)

    def clean_otp(self):
        otp = self.cleaned_data.get('otp')
        if not otp.isdigit() or len(otp) != 6:
            raise forms.ValidationError("Invalid OTP format. Please enter a 6-digit number.")
        return otp

class PasswordResetForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=254)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("There is no account associated with this email.")
        return email

class SetNewPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(), label="New Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label="Confirm New Password")

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

class DonationForm(forms.ModelForm):
    class Meta:
        model=models.BloodDonate
        fields=['age','bloodgroup','disease','unit']
