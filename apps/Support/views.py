from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from .models import FAQ, CustomerSupport, ReportIssue, SystemAlert
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import (
    FAQSerializer,
    CustomerSupportSerializer,
    ReportIssueSerializer,
    SystemAlertSerializer,
)

class FAQViewSet(ModelViewSet):
    queryset = FAQ.objects.all().order_by('-created_at')
    serializer_class = FAQSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['question', 'answer']  # Searchable fields
    filterset_fields = ['status'] 
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "message": "FAQs retrieved successfully.",
            "data": serializer.data
        })
    def get_queryset(self):
        # Filter by status or return all by default
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', None)
        status = self.request.query_params.get('status', None)
        if status in ['published', 'draft']:
            queryset= queryset.filter(status=status)
        if search:
            queryset= queryset.filter(question__icontains=search) | queryset.filter(answer__icontains=search)
        return queryset

class CustomerSupportViewSet(ModelViewSet):
    queryset = CustomerSupport.objects.all()
    serializer_class = CustomerSupportSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "message": "Customer support data retrieved successfully.",
            "data": serializer.data
        })


class ReportIssueViewSet(ModelViewSet):
    queryset = ReportIssue.objects.all().order_by('-created_at')
    serializer_class = ReportIssueSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "message": "Report issues retrieved successfully.",
            "data": serializer.data
        })


class SystemAlertViewSet(ModelViewSet):
    queryset = SystemAlert.objects.all().order_by('-date_time')
    serializer_class = SystemAlertSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "message": "System alerts retrieved successfully.",
            "data": serializer.data
        })
