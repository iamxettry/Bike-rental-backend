from rest_framework import serializers
from .models import FAQ, CustomerSupport, ReportIssue, SystemAlert

class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = '__all__'

class CustomerSupportSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerSupport
        fields = '__all__'

class ReportIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportIssue
        fields = '__all__'

class SystemAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemAlert
        fields = '__all__'
