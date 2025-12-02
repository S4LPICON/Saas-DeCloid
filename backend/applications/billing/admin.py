from django.contrib import admin

from applications.billing.models import Plan, UserSubscription

# Register your models here.
admin.site.register(Plan)  # Register your billing models here
admin.site.register(UserSubscription)  # Register your billing models here