from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from apps.common.models import UserActivity
from django.utils import timezone

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    print(f"User {user} logged in")
    UserActivity.objects.create(
        user=user,
        activity="login",
        timestamp=timezone.now(),
    )

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    print(f"User {user} logged out")
    if user:  # Check if user is authenticated
        UserActivity.objects.create(
            user=user,
            activity="logout",
            timestamp=timezone.now(),
        )
