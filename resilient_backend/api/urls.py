from django.urls import path
from .views import *

app_name = 'api'

urlpatterns = [
    path('users/', UserListCreateView.as_view(), name='user-list-create'),
    path('user/<uuid:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('user/<uuid:pk>/health_data', UserHealthDataView.as_view(), name='user-health-data'),

    path('devices/', DeviceListCreateView.as_view(), name='device-list-create'),
    path('device/<uuid:pk>/', DeviceDetailView.as_view(), name='device-detail'),

    path('scales/', ScaleListCreateView.as_view(), name='scale-list-create'),
    path('scale/<uuid:pk>/', ScaleDetailView.as_view(), name='scale-detail'),

    path('scanwatches/intra_activity/', ScanWatchIntraActivityListCreateView.as_view(), name='scanwatch-intra-list-create'),
    path('scanwatch/intra_activity/<uuid:pk>/', ScanWatchIntraActivityDetailView.as_view(), name='scanwatch-intra-list-create'),

    path('scanwatches/summary/', ScanWatchSummaryListCreateView.as_view(), name='scanwatch-intra-list-create'),
    path('scanwatch/summary/<uuid:pk>/', ScanWatchSummaryDetailView.as_view(), name='scanwatch-intra-list-create'),

    path('sleepmats/intraactivity/', SleepmatIntraActivityListCreateView.as_view(), name='sleepmat-intraactivity-list-create'),
    path('sleepmat/intraactivity/<uuid:pk>/', SleepmatIntraActivityDetailView.as_view(), name='sleepmat-intraactivity-detail'),

    path('sleepmats/summary/', SleepmatSummaryListCreateView.as_view(), name='sleepmat-summary-list-create'),
    path('sleepmat/summary/<uuid:pk>/', SleepmatSummaryDetailView.as_view(), name='sleepmat-summary-detail'),

    path('reports/', ReportListCreateView.as_view(), name='report-list-create'),
    path('report/<uuid:pk>', ReportDetailView.as_view(), name='report-detail'),

    path('usages/', UsageListCreateView.as_view(), name='usage-list-create'),
    path('usage/<uuid:pk>', UsageDetailView.as_view(), name='usage-detail'),
]