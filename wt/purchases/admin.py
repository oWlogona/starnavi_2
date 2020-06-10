from django.contrib import admin
from wt.purchases.models import Purchase


class PurchaseAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Purchase._meta.fields]


admin.site.register(Purchase, PurchaseAdmin)
