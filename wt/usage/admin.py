from django.contrib import admin
from wt.usage.models import DataUsageRecord, VoiceUsageRecord


class DataUsageRecordAdmin(admin.ModelAdmin):
    list_display = [field.name for field in DataUsageRecord._meta.fields]


class VoiceUsageRecordAdmin(admin.ModelAdmin):
    list_display = [field.name for field in VoiceUsageRecord._meta.fields]


admin.site.register(DataUsageRecord, DataUsageRecordAdmin)
admin.site.register(VoiceUsageRecord, VoiceUsageRecordAdmin)
