from django.contrib import admin

from wt.sprint_subscriptions.models import SprintSubscription


class SprintSubscriptionAdmin(admin.ModelAdmin):
    list_display = [field.name for field in SprintSubscription._meta.fields]


admin.site.register(SprintSubscription, SprintSubscriptionAdmin)
