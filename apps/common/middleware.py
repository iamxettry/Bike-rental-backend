from .utils import get_client_ip
from .models import UserActivity
from django.utils import timezone
from django.utils.timezone import localtime
from rest_framework_simplejwt.authentication import JWTAuthentication

# Track user visits
class TrackUserVisitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = None
         # Attempt to get user from the JWT token
        try:
            auth_result = self.jwt_authenticator.authenticate(request)
            if auth_result:  # If token is valid, extract user
                user, _ = auth_result
        except Exception:
            user = None 
        if not user and request.user.is_authenticated:
            user = request.user
        if user:  # Only log authenticated users
            session_key = request.session.session_key or "unknown"
            ip_address = get_client_ip(request)
            timestamp = localtime(timezone.now())
            UserActivity.objects.create(
                user=user,
                session_key=session_key,
                ip_address=ip_address,
                activity="visit",
                timestamp=timestamp,
            )

        return self.get_response(request)


# Track anonymous visits
class TrackAnonymousVisitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_authenticator = JWTAuthentication()

    def __call__(self, request):
        
        if not request.user.is_authenticated:  # Only log unauthenticated users
            session_key = request.session.session_key or "unknown"
            ip_address = get_client_ip(request)
            timestamp = localtime(timezone.now())
            UserActivity.objects.create(
                session_key=session_key,
                ip_address=ip_address,
                activity="anonymous_visit",
                timestamp=timestamp,
            )
        return self.get_response(request)
