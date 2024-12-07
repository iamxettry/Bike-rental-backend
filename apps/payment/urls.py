from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InitiatePaymentView,VerifyPaymentView,EsewaRequestView,EsewaPaymentViewSet
router = DefaultRouter()
router.register(r'esewa', EsewaPaymentViewSet)

urlpatterns = [
    path('initiate/', InitiatePaymentView.as_view(), name='initiate-payment-api'),
    path('verify/', VerifyPaymentView.as_view(), name='verify-payment-api'),

    # E-sewa
    path('esewarequest/', EsewaRequestView.as_view(), name='initiate-esewa-api'),
    path('esewa-verify/', InitiatePaymentView.as_view(), name='verify-esewa-api'),
     path('', include(router.urls)),

]