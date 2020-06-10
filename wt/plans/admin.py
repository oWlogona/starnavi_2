from django.contrib import admin
from wt.plans.models import Plan


class PlanAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Plan._meta.fields]


admin.site.register(Plan, PlanAdmin)
