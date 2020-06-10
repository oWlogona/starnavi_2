from django.contrib import admin
from wt.att_subscriptions.models import ATTSubscription


class ATTSubscriptionAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ATTSubscription._meta.fields]


admin.site.register(ATTSubscription, ATTSubscriptionAdmin)
