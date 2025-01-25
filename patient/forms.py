from django import forms
from django.contrib.auth.models import User
from . import models


class PatientUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), label="Password")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']

    def clean_email(self):
        """Ensure the email is unique."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email



class PatientForm(forms.ModelForm):
    class Meta:
        model = models.Patient
        fields = ['age', 'bloodgroup', 'disease', 'address', 'doctorname', 'mobile', 'profile_pic']


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
