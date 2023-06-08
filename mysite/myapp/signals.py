from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile
from django.contrib.auth import get_user_model


@receiver(user_logged_in)
def create_profile(sender, user, request, **kwargs):
    User = get_user_model()
    try:
        profile = user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=user)
    
    # Set the profile picture if it doesn't exist
    if not profile.image:
        profile.image = 'profile/profilepic.gif'  # Update with the desired image path
        profile.save()


@receiver(post_save, sender=User)
def build_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()


