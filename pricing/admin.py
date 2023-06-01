from django.contrib import admin
from .models import Plan, Feature, PaymentDetail, CreatorDisputeCount

admin.site.register(Feature)


# Register your models here.
@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_filter = ['active', 'disputes', 'currency']
    search_fields = ['id', 'name', 'price', 'stripe_product_id']
    list_display = ['name', 'description', 'price', 'currency', 'disputes', 'active', 'created_at', 'updated_at',
                    'stripe_product_id']


@admin.register(PaymentDetail)
class PaymentDetailAdmin(admin.ModelAdmin):
    list_filter = ['stripe_payment_status', 'is_subscription_active']
    search_fields = ['stripe_payment_id', 'plan']
    list_display = ['creator', 'plan', 'stripe_payment_status', 'stripe_payment_id', 'is_subscription_active',
                    'created_at', 'updated_at']


@admin.register(CreatorDisputeCount)
class CreatorDisputeCountAdmin(admin.ModelAdmin):
    search_fields = ['creator']
    list_display = ['creator', 'disputes_created', 'disputes_available']
