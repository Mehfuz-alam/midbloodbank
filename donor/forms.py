from django import forms
from django.contrib.auth.models import User
from . import models
from .models import Donor

class DonorUserForm(forms.ModelForm):
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password', 'email']

class DonorForm(forms.ModelForm):
    class Meta:
        model = Donor
        fields = ['address', 'mobile', 'profile_pic']

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
