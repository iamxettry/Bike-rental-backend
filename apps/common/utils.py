
from django.conf import settings
from django.core.mail import send_mail
from apps.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
# Function to generate the token for the user
def get_tokens_for_user(user):
    if not isinstance(user, User):
        raise ValueError("The user must be an instance of User.")
    refresh = RefreshToken.for_user(user)
    access_token = refresh.access_token
    access_token['username'] = user.username
    access_token['email'] = user.email
    access_token['is_superuser'] = user.is_superuser
    return {
        "refresh": str(refresh),
        "access": str(access_token),
    }



def send_otp_email(subject, message, to_email):
    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER, 
            [to_email],
            fail_silently=False,
        )
        print(f'Successfully sent OTP email to {to_email}')
        return True
    except Exception as e:
        print(f"Failed to send OTP email: {str(e)}")
        return False

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
