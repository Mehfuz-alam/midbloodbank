from celery import shared_task
from .models import BloodDonate
from datetime import timedelta
from django.utils.timezone import now

@shared_task
def delete_expired_donations():
    expired_donations = BloodDonate.objects.filter(date__lt=now().date() - timedelta(days=35))
    expired_donations.delete()
