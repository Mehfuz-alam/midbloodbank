from django import forms
from django.contrib.auth.models import User
from . import models
from django.core.exceptions import ValidationError

class PatientUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), label="Password")
    latitude = forms.FloatField(widget=forms.HiddenInput())
    longitude = forms.FloatField(widget=forms.HiddenInput())
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']

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


class PatientForm(forms.ModelForm):
    latitude = forms.FloatField(widget=forms.HiddenInput())
    longitude = forms.FloatField(widget=forms.HiddenInput())
    class Meta:
        model = models.Patient
        fields = ['age', 'bloodgroup', 'disease','doctorname', 'address', 'mobile', 'profile_pic']
    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        if len(mobile) != 10 or not mobile.isdigit():
            raise ValidationError("Phone number must be exactly 10 digits long.")
        return mobile

class PasswordResetForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=254)

    def clean_email(self):
        """Ensure the email exists in the database."""
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("There is no account associated with this email.")
        return email


class OTPVerificationForm(forms.Form):
    otp = forms.CharField(label="Enter OTP", max_length=6)

    def clean_otp(self):
        """Validate OTP is a 6-digit number."""
        otp = self.cleaned_data.get('otp')
        if not otp.isdigit() or len(otp) != 6:
            raise forms.ValidationError("Invalid OTP format. Please enter a 6-digit number.")
        return otp


class SetNewPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(), label="New Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label="Confirm New Password")

    def clean(self):
        """Validate that both passwords match."""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data
