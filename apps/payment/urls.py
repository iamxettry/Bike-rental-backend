from django.urls import path
from .views import InitiatePaymentView,VerifyPaymentView,EsewaRequestView

urlpatterns = [
    path('initiate/', InitiatePaymentView.as_view(), name='initiate-payment-api'),
    path('verify/', VerifyPaymentView.as_view(), name='verify-payment-api'),

    # E-sewa
    path('esewarequest/', EsewaRequestView.as_view(), name='initiate-esewa-api'),
    path('esewa-verify/', InitiatePaymentView.as_view(), name='verify-esewa-api'),

]