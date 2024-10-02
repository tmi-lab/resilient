from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def validate_username(self, value):
        """
        Validate that the username is not already in use.
        """
        if User.objects.filter(username=value).exists():
            res = serializers.ValidationError({
                "status_code": 403,
                "message": "This username is already in use. Please choose a different one."
            })
            raise res

        return value
    
    def to_representation(self, instance):
        """
        Customize the representation of the serialized data.
        """
        # Only include specific fields in the response
        return {
            'id': instance.id,
            'username': instance.username,
            'role': instance.role,
            'created_at': instance.created_at,
            'updated_at': instance.updated_at,
            'active': instance.active,
            'withings_connected': instance.withings_connected,
            'withings_credentials_path': instance.withings_credentials_path,
            'scale_device': instance.scale_device_id,
            'sleepmat_device': instance.sleepmat_device_id,
            'scanwatch_device': instance.scanwatch_device_id,
        }

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = '__all__'

    def validate_device_hash(self, value):
        """
        Validate that the device_hash is not already in use.
        """
        if Device.objects.filter(device_hash=value).exists():
            raise serializers.ValidationError("This device_hash is already in use. Please choose a different one.")
        return value
    
    def validate_device_type(self, value):
        valid_device_types = ['scale', 'scan_watch', 'sleep_mat']

        if value in valid_device_types:
            return value
        raise serializers.ValidationError("{0} is not an accepted type: {1}".format(value, ", ".join(valid_device_types)))
    
class ScaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scale
        fields = '__all__'

class ScanWatchIntraActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ScanWatchIntraActivity
        fields = '__all__'

class ScanWatchSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = ScanWatchSummary
        fields = '__all__'

class SleepmatIntraActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = SleepmatIntraActivity
        fields = '__all__'

class SleepmatSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = SleepmatSummary
        fields = '__all__'

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'

class UsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usage
        fields = '__all__'

class UserHealthDataSerializer(serializers.ModelSerializer):
    scanwatch_summary = ScanWatchSummarySerializer(many=True, read_only=True)
    scanwatch_intraactivity = ScanWatchIntraActivitySerializer(many=True, read_only=True)
    sleepmat_summary = SleepmatSummarySerializer(many=True, read_only=True)
    sleepmat_intraactivity = SleepmatIntraActivitySerializer(many=True, read_only=True)
    scale =  ScaleSerializer(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = ['id',
                  'username',
                  'role',
                  'created_at',
                  'updated_at',
                  'scanwatch_summary',
                  'scanwatch_intractivty',
                  'sleepmat_summary',
                  'sleepmat_intraactivity',
                  'scale'
                  ]