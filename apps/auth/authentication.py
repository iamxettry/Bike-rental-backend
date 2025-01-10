from rest_framework_simplejwt.authentication import JWTAuthentication
from apps.common.models import UserActivity
from django.utils.timezone import now

class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        user_auth_tuple = super().authenticate(request)
        if user_auth_tuple is not None:
            user, _ = user_auth_tuple
            if user.is_authenticated:
                # Log user activity
                UserActivity.objects.create(
                    user=user,
                    activity="login",
                    timestamp=now(),
                )
        return user_auth_tuple
