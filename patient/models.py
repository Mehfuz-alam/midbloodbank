from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta
from geopy.geocoders import Nominatim

class Patient(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    
    profile_pic= models.ImageField(upload_to='profile_pic/Patient/',null=True,blank=True)

    age=models.PositiveIntegerField()
    bloodgroup=models.CharField(max_length=10)
    disease=models.CharField(max_length=100)
    doctorname=models.CharField(max_length=50)

    address = models.CharField(max_length=40)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    mobile = models.CharField(max_length=20,null=False)
    
   
    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name
    @property
    def get_instance(self):
        return self
    def __str__(self):
        return self.user.first_name
    @property
    def location_name(self):
        """Convert latitude and longitude into a readable address."""
        if self.latitude and self.longitude:
            geolocator = Nominatim(user_agent="donor_location_geocoder")
            location = geolocator.reverse((self.latitude, self.longitude), exactly_one=True)
            return location.address if location else "Location not found"
        return "No location available"

class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="patient_otp")  # Added related_name
    otp_code = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        """Check if the OTP is still valid (e.g., valid for 10 minutes)."""
        return now() < self.created_at + timedelta(minutes=10)

    def __str__(self):
        return f"OTP for {self.user.username}: {self.otp_code}"

