from rest_framework import serializers
from .models import Plan, Feature, PaymentDetail, CreatorDisputeCount


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ['id', 'text']


class GetPlanSerializer(serializers.ModelSerializer):
    feature = FeatureSerializer(source='feature.all', many=True)

    class Meta:
        model = Plan
        fields = ['id', 'name', 'description', 'disputes', 'price', 'currency', 'active', 'feature',
                  'stripe_product_id', 'created_at', 'updated_at']


class CreatePlanSerializer(serializers.ModelSerializer):
    stripe_product_id = serializers.CharField(required=False)

    class Meta:
        model = Plan
        fields = ['id', 'name', 'description', 'disputes', 'price', 'currency', 'active', 'feature',
                  'stripe_product_id', 'created_at', 'updated_at']


class PaymentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentDetail
        fields = ['id', 'creator', 'plan', 'stripe_payment_status', 'stripe_payment_id', 'is_subscription_active',
                  'created_at', 'updated_at']


class CreatorDisputeCountSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreatorDisputeCount
        fields = ['id', 'creator', 'disputes_created', 'disputes_available']
