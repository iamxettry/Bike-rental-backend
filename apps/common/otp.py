from apps.auth.models import User
from django.utils.crypto import get_random_string
from django.utils import timezone
from .utils import send_otp_email
import os

class OTPAction:
    LOGIN = 'Login'
    RESET = 'Reset'

class OTPhandlers:

    def __init__(
            self,
            request,
            user:User,
            action = OTPAction.LOGIN,
            valid_period=int(os.environ.get('OTP_VALID_PERIOD'))
        ):
        self.request = request
        self.user = user
        self.action = action
        self.valid_period = valid_period

    def generate_otp(self):
        otp = get_random_string(length=6,allowed_chars="0123456789")
        self.user.otp = otp
        self.user.otp_created_at = timezone.now()
        self.user.otp_tries = 0
        self.user.save()
        return otp,self.user.otp_created_at
    
    def verify_otp(self,otp):
        if self.action == OTPAction.LOGIN and self.user.email_verified:
            return False, "Email is already verified."
        
        if self.user.otp_tries >= 3:
            return False, "OTP Tried too many times"
        if self.user.otp != otp:
            self.user.otp_tries += 1 
            self.user.save()
            if self.user.otp_tries >= 3:
                return False, "OTP Tried too many times"
            
            return False,"Invalid OTP"
        
        if (
            self.user.otp_created_at
            and self.user.otp_created_at + timezone.timedelta(minutes=self.valid_period)
            < timezone.now()
        ):
            return False, "OTP expired"

        
        self.user.otp = None
        self.user.otp_tries = 0
        self.user.otp_created_at = None
        if self.action == OTPAction.LOGIN:
            self.user.email_verified = True
            self.user.email_verified_date = timezone.now()
        self.user.save()
        return True, "OTP Verified"
        
    def send_otp(self):
        otp,otp_created_at = self.generate_otp()
        subject = f'{self.action} OTP'
        receiver = self.user.email
        if self.action == OTPAction.LOGIN:
            message = f'Hi @{self.user.username},\n\nYour {self.action} OTP is: {otp}'
        else:
            random_password = get_random_string(length=8,allowed_chars='123456789asdfghjklqwertyuiopzxcvbnm')
            message = f'Hi @{self.user.username},\n\nYour {self.action} password OTP is: {otp}\n\nPlease use this OTP to reset your password\nYour new password is : {random_password}'

            self.user.set_password(random_password)
            self.user.save()

        if not send_otp_email(subject, message, receiver):
            return False, "Failed to send OTP email",otp_created_at
        
        return True, "OTP sent successfully",otp_created_at