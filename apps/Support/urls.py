from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FAQViewSet, CustomerSupportViewSet, ReportIssueViewSet, SystemAlertViewSet

router = DefaultRouter()
router.register('faqs', FAQViewSet, basename='faq')
router.register('customer-support', CustomerSupportViewSet, basename='customer-support')
router.register('report-issues', ReportIssueViewSet, basename='report-issue')
router.register('system-alerts', SystemAlertViewSet, basename='system-alert')

urlpatterns = [
    path('', include(router.urls)),
]
