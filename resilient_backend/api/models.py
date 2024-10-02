from django.db import models
from django.utils import timezone
import uuid

class Device(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device_hash = models.CharField(max_length=100)
    device_type = models.CharField(max_length=100)
    mac_address = models.CharField(max_length=100)
    is_active = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def save(self, *args, **kwargs):
        # Update the `updated_at` field before saving the record
        self.updated_at = timezone.now()
        super(Device, self).save(*args, **kwargs)

class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=50)
    role = models.CharField(max_length=100)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    password_hash = models.CharField(max_length=200)
    active = models.BooleanField(default=True)
    withings_connected = models.BooleanField(default=False)
    withings_credentials_path = models.CharField(max_length=300, null=True, blank=True)
    scale_device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='scale_device_id', null=True, blank=True)
    sleepmat_device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='sleepmat_device_id', null=True, blank=True)
    scanwatch_device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='scanwatch_device_id', null=True, blank=True)

    def save(self, *args, **kwargs):
        # Update the `updated_at` field before saving the record
        self.updated_at = timezone.now()
        super(User, self).save(*args, **kwargs)

class Scale(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='scales')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scales_user')
    date = models.DateTimeField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    muscle_mass = models.FloatField(null=True, blank=True)
    bone_mass = models.FloatField(null=True, blank=True)
    fat_mass = models.FloatField(null=True, blank=True)

class ScanWatchIntraActivity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='scanwatch_intraactivity')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scanwatch_intraactivity_user')
    heart_rate = models.FloatField(null=True, blank=True)
    date_heart_rate = models.FloatField(null=True, blank=True)
    steps = models.FloatField(null=True, blank=True)
    date_steps = models.FloatField(null=True, blank=True)
    calories = models.FloatField(null=True, blank=True)
    date_calories = models.FloatField(null=True, blank=True)

class ScanWatchSummary(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='scanwatch_summary')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scanwatch_summary_user')
    date = models.DateField(null=True, blank=True)
    average_heart_rate = models.FloatField(null=True, blank=True)
    calories = models.FloatField(null=True, blank=True)
    steps = models.FloatField(null=True, blank=True)
    hr_max = models.FloatField(null=True, blank=True)
    hr_min = models.FloatField(null=True, blank=True)

class SleepmatIntraActivity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='sleepmat_intraactivity')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sleepmat_intraactivity_user')
    start_date = models.FloatField(null=True, blank=True) 
    end_date = models.FloatField(null=True, blank=True)
    sleep_state = models.IntegerField(null=True, blank=True) 
    date_heart_rate = models.FloatField(null=True, blank=True)
    heart_rate = models.FloatField(null=True, blank=True)
    date_respiration_rate = models.FloatField(null=True, blank=True)
    respiration_rate = models.FloatField(null=True, blank=True)
    date_snoring = models.FloatField(null=True, blank=True)
    snoring = models.FloatField(null=True, blank=True)
    date_sdnn_1 = models.FloatField(null=True, blank=True)
    sdnn_1 = models.FloatField(null=True, blank=True)

class SleepmatSummary(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='sleepmat_summary')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sleepmat_summary_user')
    date = models.DateField(null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True) 
    end_date = models.DateTimeField(null=True, blank=True)
    breathing_disturbances = models.IntegerField(null=True, blank=True)
    deep_sleep_duration = models.FloatField(null=True, blank=True)
    duration_to_sleep = models.FloatField(null=True, blank=True)
    duration_to_wakeup = models.FloatField(null=True, blank=True)
    average_heart_rate = models.FloatField(null=True, blank=True)
    light_sleep_duration = models.FloatField(null=True, blank=True)
    rem_sleep_duration = models.FloatField(null=True, blank=True)
    average_rr = models.IntegerField(null=True, blank=True)
    sleep_score = models.FloatField(null=True, blank=True)
    wakeup_count = models.FloatField(null=True, blank=True)
    wakeup_duration = models.FloatField(null=True, blank=True)
    total_sleep_time = models.FloatField(null=True, blank=True)
    total_time_in_bed = models.FloatField(null=True, blank=True)
    awake_in_bed = models.FloatField(null=True, blank=True)
    apnea = models.FloatField(null=True, blank=True)
    out_of_bed_count = models.FloatField(null=True, blank=True)
    hr_date_af = models.DateTimeField(null=True, blank=True)
    hr_af = models.FloatField(null=True, blank=True)
    hr_date_rr = models.DateTimeField(null=True, blank=True)
    hr_rr = models.FloatField(null=True, blank=True)


class Report(models.Model):
    id =  models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    path = models.CharField(max_length=300)
    type = models.CharField(max_length=20, default='aggegated') # e.g., 'weekly', 'global'
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def save(self, *args, **kwargs):
        # Update the `updated_at` field before saving the record
        self.updated_at = timezone.now()
        super(Report, self).save(*args, **kwargs)

class Usage(models.Model):
    id =  models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='usages')
    scanwatch_usage_level = models.CharField(max_length=10, null=True, blank=True)
    scanwatch_battery = models.CharField(max_length=10, null=True, blank=True)
    scanwatch_last_date = models.DateField(null=True, blank=True)
    sleepmat_usage_level = models.CharField(max_length=10, null=True, blank=True)
    sleepmat_battery = models.CharField(max_length=10, null=True, blank=True)
    sleepmat_last_date = models.DateField(null=True, blank=True)
    scale_usage_level = models.CharField(max_length=10, null=True, blank=True)
    scale_battery = models.CharField(max_length=10, null=True, blank=True)
    scale_last_date = models.DateField(null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Update the `updated_at` field before saving the record
        self.updated_at = timezone.now()
        super(Usage, self).save(*args, **kwargs)
    