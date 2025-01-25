from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta

class Donor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=15, null=True)
    profile_pic = models.ImageField(upload_to='profile_pic/DonorProfilePic/', null=True, blank=True)

    @property
    def get_name(self):
        return self.user.first_name + ' ' + self.user.last_name

    @property
    def get_instance(self):
        return self

class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="donor_otp")  # Added related_name
    otp_code = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        """Check if the OTP is still valid (e.g., valid for 10 minutes)."""
        return now() < self.created_at + timedelta(minutes=10)

    def __str__(self):
        return f"OTP for {self.user.username}: {self.otp_code}"


class BloodDonate(models.Model): 
    donor=models.ForeignKey(Donor,on_delete=models.CASCADE)   
    disease=models.CharField(max_length=100,default="Nothing")
    age=models.PositiveIntegerField()
    bloodgroup=models.CharField(max_length=10)
    unit=models.PositiveIntegerField(default=0)
    status=models.CharField(max_length=20,default="Pending")
    date=models.DateField(auto_now=True)
    def __str__(self):
        return self.donor