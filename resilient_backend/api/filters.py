import django_filters
from django.db.models import Q
from .models import *

class UserFilter(django_filters.FilterSet):
    id = django_filters.UUIDFilter(field_name='id', lookup_expr='exact')
    username = django_filters.CharFilter(field_name='username', lookup_expr='exact') 
    role = django_filters.CharFilter(field_name='role', lookup_expr='exact')
    created_at = django_filters.DateFilter(field_name='created_at', lookup_expr='exact')
    created_at_from = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_at_to = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    updated_at = django_filters.DateFilter(field_name='updated_at', lookup_expr='exact')
    updated_at_from = django_filters.DateFilter(field_name='updated_at', lookup_expr='gte')
    updated_at_to = django_filters.DateFilter(field_name='updated_at', lookup_expr='lte')
    active = django_filters.BooleanFilter(field_name='active', lookup_expr='exact')
    withings_connected = django_filters.BooleanFilter(field_name='withings_connected', lookup_expr='exact')
    scale_device = django_filters.UUIDFilter(field_name='scale_device_id', lookup_expr='exact')
    sleepmat_device = django_filters.UUIDFilter(field_name='sleepmat_device_id', lookup_expr='exact')
    scanwatch_device = django_filters.UUIDFilter(field_name='scanwatch_device_id', lookup_expr='exact')

    class Meta:
        model = User
        fields = [ 'id', 
                    'role', 
                    'username', 
                    'created_at', 
                    'updated_at', 
                    'active', 
                    'withings_connected',
                    'scale_device',
                    'sleepmat_device',
                    'scanwatch_device'
                ]

class DeviceFilter(django_filters.FilterSet):
    id = django_filters.UUIDFilter(field_name='id', lookup_expr='exact')
    device_hash = django_filters.CharFilter(field_name='device_hash', lookup_expr='exact')
    device_type = django_filters.CharFilter(field_name='device_type', lookup_expr='exact')
    mac_address = django_filters.CharFilter(field_name='mac_address', lookup_expr='exact')
    is_active = django_filters.BooleanFilter(field_name='is_active', lookup_expr='exact')
    created_at = django_filters.DateFilter(field_name='created_at', lookup_expr='exact')
    created_at_from = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_at_to = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    updated_at = django_filters.DateFilter(field_name='updated_at', lookup_expr='exact')
    updated_at_from = django_filters.DateFilter(field_name='updated_at', lookup_expr='gte')
    updated_at_to = django_filters.DateFilter(field_name='updated_at', lookup_expr='lte')
    username = django_filters.CharFilter(method='filter_by_username')

    class Meta:
        model = Device
        fields = []

    def filter_by_username(self, queryset, name, value):
        return queryset.filter(
            Q(scale_device_id__username=value) |
            Q(sleepmat_device_id__username=value) |
            Q(scanwatch_device_id__username=value)
        )

class ScaleFilter(django_filters.FilterSet):
    id = django_filters.UUIDFilter(field_name='id', lookup_expr='exact')
    device_id = django_filters.UUIDFilter(field_name='device_id', lookup_expr='exact')
    user_id = django_filters.UUIDFilter(field_name='user_id', lookup_expr='exact')
    date = django_filters.DateFilter(field_name='date', lookup_expr='exact')
    date_from = django_filters.DateFilter(field_name='date', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='date', lookup_expr='lte')
    username = django_filters.CharFilter(field_name='user__username', lookup_expr='exact')

    class Meta:
        model = Scale
        fields = []

class ScanWatch_IntraActivityFilter(django_filters.FilterSet):
    id = django_filters.UUIDFilter(field_name='id', lookup_expr='exact')
    device_id = django_filters.UUIDFilter(field_name='device_id', lookup_expr='exact')
    user_id = django_filters.UUIDFilter(field_name='user_id', lookup_expr='exact')
    heart_rate = django_filters.RangeFilter(field_name='heart_rate')
    date_heart_rate = django_filters.RangeFilter(field_name='date_heart_rate')
    steps = django_filters.RangeFilter(field_name='steps')
    date_steps = django_filters.RangeFilter(field_name='date_steps')
    calories = django_filters.RangeFilter(field_name='calories')
    date_calories = django_filters.RangeFilter(field_name='date_calories')
    username = django_filters.CharFilter(field_name='user__username', lookup_expr='exact')

    class Meta:
        model = ScanWatchIntraActivity
        fields = []

class ScanWatch_SummaryFilter(django_filters.FilterSet):
    id = django_filters.UUIDFilter(field_name='id', lookup_expr='exact')
    device_id = django_filters.UUIDFilter(field_name='device_id', lookup_expr='exact')
    user_id = django_filters.UUIDFilter(field_name='user_id', lookup_expr='exact')
    date_from = django_filters.DateFilter(field_name='date', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='date', lookup_expr='lte')
    average_heart_rate = django_filters.RangeFilter(field_name='average_heart_rate')
    calories = django_filters.RangeFilter(field_name='calories')
    steps = django_filters.RangeFilter(field_name='steps')
    username = django_filters.CharFilter(field_name='user__username', lookup_expr='exact')

    class Meta:
        model = ScanWatchSummary
        fields = []

class Sleepmat_IntraActivityFilter(django_filters.FilterSet):
    id = django_filters.UUIDFilter(field_name='id', lookup_expr='exact')
    device_id = django_filters.UUIDFilter(field_name='device_id', lookup_expr='exact')
    user_id = django_filters.UUIDFilter(field_name='user_id', lookup_expr='exact')
    start_date_from = django_filters.DateFilter(field_name='start_date', lookup_expr='gte')
    start_date_to = django_filters.DateFilter(field_name='start_date', lookup_expr='lte')
    end_date_from = django_filters.DateFilter(field_name='end_date', lookup_expr='gte')
    end_date_to = django_filters.DateFilter(field_name='end_date', lookup_expr='lte')
    sleep_state = django_filters.CharFilter(field_name='sleep_state', lookup_expr='exact')
    date_heart_rate = django_filters.RangeFilter(field_name='date_heart_rate')
    heart_rate = django_filters.RangeFilter(field_name='heart_rate')
    date_respiration_rate = django_filters.RangeFilter(field_name='date_respiration_rate')
    respiration_rate = django_filters.RangeFilter(field_name='respiration_rate')
    date_snoring = django_filters.RangeFilter(field_name='date_snoring')
    snoring = django_filters.RangeFilter(field_name='snoring')
    date_sdnn_1 = django_filters.RangeFilter(field_name='date_sdnn_1')
    sdnn_1 = django_filters.RangeFilter(field_name='sdnn_1')
    username = django_filters.CharFilter(field_name='user__username', lookup_expr='exact')

    class Meta:
        model = SleepmatIntraActivity
        fields = []

class Sleepmat_SummaryFilter(django_filters.FilterSet):
    id = django_filters.UUIDFilter(field_name='id', lookup_expr='exact')
    device_id = django_filters.UUIDFilter(field_name='device_id', lookup_expr='exact')
    user_id = django_filters.UUIDFilter(field_name='user_id', lookup_expr='exact')
    date_from = django_filters.DateFilter(field_name='date', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='date', lookup_expr='lte')
    breathing_disturbances = django_filters.RangeFilter(field_name='breathing_disturbances')
    deep_sleep_duration = django_filters.RangeFilter(field_name='deep_sleep_duration')
    duration_to_sleep = django_filters.RangeFilter(field_name='duration_to_sleep')
    duration_to_wakeup = django_filters.RangeFilter(field_name='duration_to_wakeup')
    average_heart_rate = django_filters.RangeFilter(field_name='average_heart_rate')
    light_sleep_duration = django_filters.RangeFilter(field_name='light_sleep_duration')
    rem_sleep_duration = django_filters.RangeFilter(field_name='rem_sleep_duration')
    average_rr = django_filters.RangeFilter(field_name='average_rr')
    sleep_score = django_filters.RangeFilter(field_name='sleep_score')
    wakeup_count = django_filters.RangeFilter(field_name='wakeup_count')
    wakeup_duration = django_filters.RangeFilter(field_name='wakeup_duration')
    username = django_filters.CharFilter(field_name='user__username', lookup_expr='exact')

    class Meta:
        model = SleepmatSummary
        fields = []

class ReportFilter(django_filters.FilterSet):
    id = django_filters.UUIDFilter(field_name='id', lookup_expr='exact')
    user_id = django_filters.UUIDFilter(field_name='user_id', lookup_expr='exact')
    start_date_from = django_filters.DateFilter(field_name='date', lookup_expr='gte')
    start_date_to = django_filters.DateFilter(field_name='date', lookup_expr='lte')
    end_date_from = django_filters.DateFilter(field_name='date', lookup_expr='gte')
    end_date_to = django_filters.DateFilter(field_name='date', lookup_expr='lte')
    created_at_from = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_at_to = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    updated_at_from = django_filters.DateFilter(field_name='updated_at', lookup_expr='gte')
    updated_at_to = django_filters.DateFilter(field_name='updated_at', lookup_expr='lte')
    username = django_filters.CharFilter(field_name='user__username', lookup_expr='exact')

    class Meta:
        model = Report
        fields = []

class UsageFilter(django_filters.FilterSet):
    id = django_filters.UUIDFilter(field_name='id', lookup_expr='exact')
    user_id = django_filters.UUIDFilter(field_name='user_id', lookup_expr='exact')
    report_id = django_filters.UUIDFilter(field_name='report_id', lookup_expr='exact')
    scanwatch_usage_level = django_filters.CharFilter(field_name='scanwatch_usage_level', lookup_expr='exact')
    scanwatch_battery = django_filters.RangeFilter(field_name='scanwatch_battery')
    scanwatch_last_date_from = django_filters.DateFilter(field_name='scanwatch_last_date', lookup_expr='gte')
    scanwatch_last_date_to = django_filters.DateFilter(field_name='scanwatch_last_date', lookup_expr='lte')
    sleepmat_usage_level = django_filters.CharFilter(field_name='sleepmat_usage_level', lookup_expr='exact')
    sleepmat_battery = django_filters.RangeFilter(field_name='sleepmat_battery')
    sleepmat_last_date_from = django_filters.DateFilter(field_name='sleepmat_last_date', lookup_expr='gte')
    sleepmat_last_date_to = django_filters.DateFilter(field_name='sleepmat_last_date', lookup_expr='lte')
    scale_usage_level = django_filters.CharFilter(field_name='scale_usage_level', lookup_expr='exact')
    scale_battery = django_filters.RangeFilter(field_name='scale_battery')
    scale_last_date_from = django_filters.DateFilter(field_name='scale_last_date', lookup_expr='gte')
    scale_last_date_to = django_filters.DateFilter(field_name='scale_last_date', lookup_expr='lte')


    class Meta:
        model = Usage
        fields = []