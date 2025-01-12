from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InitiatePaymentView,VerifyPaymentView,EsewaRequestView,EsewaPaymentViewSet, PaymentStatsView, MonthlyPaymentStatsView, PaymentListView
router = DefaultRouter()
router.register(r'esewa', EsewaPaymentViewSet, basename="esewa-payment")

urlpatterns = [
    path('initiate/', InitiatePaymentView.as_view(), name='initiate-payment-api'),
    path('verify/', VerifyPaymentView.as_view(), name='verify-payment-api'),

    # E-sewa
    path('esewarequest/', EsewaRequestView.as_view(), name='initiate-esewa-api'),
    path('esewa-verify/', InitiatePaymentView.as_view(), name='verify-esewa-api'),
     path('', include(router.urls)),

    #  quick stats
    path('quick-stats/', PaymentStatsView.as_view(), name='payment-stats-api'),
    path('monthly-payment-history/', MonthlyPaymentStatsView.as_view(), name='monthly-payment-history-api'),
     path('list/', PaymentListView.as_view(), name='payment-list-api'), 

]