from django.http import JsonResponse
from rest_framework import generics
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import *
from .serializers import *
from .filters import *
import uuid

class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filterset_class = UserFilter
    filter_backends = [DjangoFilterBackend]

    def perform_create(self, serializer):
        # Generate a new UUID before saving the instance
        serializer.save(id=uuid.uuid4())

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return JsonResponse({"users": serializer.data})

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserHealthDataView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserHealthDataSerializer

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        scanwatch_summary = ScanWatchSummary.objects.filter(device__user=user)
        scanWatch_intraactivity = ScanWatchIntraActivity.objects.filter(device__user=user)
        sleepmat_summary = SleepmatSummary.objects.filter(device__user=user)
        sleepmat_intraactivity = SleepmatIntraActivity.objects.filter(device__user=user)
        scale = Scale.objects.filter(device__user=user)
        
        data = {
            'user': UserSerializer(user).data,
            'scale' : ScaleSerializer(scale, many=True).data,
            'scanwatch_summary': ScanWatchSummarySerializer(scanwatch_summary, many=True).data,
            'scanwatch_intraactivity': ScanWatchIntraActivitySerializer(scanWatch_intraactivity, many=True).data,
            'sleepmat_summary': SleepmatSummarySerializer(sleepmat_summary, many=True).data,
            'sleepmat_intraactivity':  SleepmatIntraActivitySerializer(sleepmat_intraactivity, many=True).data
        }

        return JsonResponse({'health_data': data})

class DeviceListCreateView(generics.ListCreateAPIView):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    filterset_class = DeviceFilter
    filter_backends = [DjangoFilterBackend]

    def perform_create(self, serializer):
        # Generate a new UUID before saving the instance
        serializer.save(id=uuid.uuid4())

    def list(self, request, *args, **kwargs):            
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({"devices": serializer.data})

class DeviceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer

class ScaleListCreateView(generics.ListCreateAPIView):
    queryset = Scale.objects.all()
    serializer_class = ScaleSerializer
    filterset_class = ScaleFilter
    filter_backends = [DjangoFilterBackend]

    def perform_create(self, serializer):
        # Generate a new UUID before saving the instance
        serializer.save(id=uuid.uuid4())

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({"scales": serializer.data})
    
class ScaleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Scale.objects.all()
    serializer_class = ScaleSerializer
    
class ScanWatchIntraActivityListCreateView(generics.ListCreateAPIView):
    queryset = ScanWatchIntraActivity.objects.all()
    serializer_class = ScanWatchIntraActivitySerializer
    filterset_class = ScanWatch_IntraActivityFilter
    filter_backends = [DjangoFilterBackend]

    def perform_create(self, serializer):
        # Generate a new UUID before saving the instance
        serializer.save(id=uuid.uuid4())

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({"scanwatches_intraactivity": serializer.data})
    
class ScanWatchIntraActivityDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Scale.objects.all()
    serializer_class = ScanWatchIntraActivitySerializer

class ScanWatchSummaryListCreateView(generics.ListCreateAPIView):
    queryset = ScanWatchSummary.objects.all()
    serializer_class = ScanWatchSummarySerializer
    filterset_class = ScanWatch_SummaryFilter
    filter_backends = [DjangoFilterBackend]

    def perform_create(self, serializer):
        # Generate a new UUID before saving the instance
        serializer.save(id=uuid.uuid4())

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({"scanwatches_summary": serializer.data})
    
class ScanWatchSummaryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Scale.objects.all()
    serializer_class = ScanWatchIntraActivitySerializer

class SleepmatIntraActivityListCreateView(generics.ListCreateAPIView):
    queryset = SleepmatIntraActivity.objects.all()
    serializer_class = SleepmatIntraActivitySerializer
    filterset_class = Sleepmat_IntraActivityFilter
    filter_backends = [DjangoFilterBackend]

    def perform_create(self, serializer):
        # Generate a new UUID before saving the instance
        serializer.save(id=uuid.uuid4())

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({"sleepmats_intraactivity": serializer.data})

class SleepmatIntraActivityDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SleepmatIntraActivity.objects.all()
    serializer_class = SleepmatIntraActivitySerializer

class SleepmatSummaryListCreateView(generics.ListCreateAPIView):
    queryset = SleepmatSummary.objects.all()
    serializer_class = SleepmatSummarySerializer
    filterset_class = Sleepmat_SummaryFilter
    filter_backends = [DjangoFilterBackend]

    def perform_create(self, serializer):
        # Generate a new UUID before saving the instance
        serializer.save(id=uuid.uuid4())

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({"sleepmats_summary": serializer.data})

class SleepmatSummaryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SleepmatSummary.objects.all()
    serializer_class = SleepmatSummarySerializer

class ReportListCreateView(generics.ListCreateAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    filterset_class = ReportFilter
    filter_backends = [DjangoFilterBackend]

    def perform_create(self, serializer):
        # Generate a new UUID before saving the instance
        serializer.save(id=uuid.uuid4())

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({"reports": serializer.data})
    
class ReportDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer

class UsageListCreateView(generics.ListCreateAPIView):
    queryset = Usage.objects.all()
    serializer_class = UsageSerializer
    filterset_class = UsageFilter
    filter_backends = [DjangoFilterBackend]

    def perform_create(self, serializer):
        # Generate a new UUID before saving the instance
        serializer.save(id=uuid.uuid4())

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({"usages": serializer.data})

class UsageDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer