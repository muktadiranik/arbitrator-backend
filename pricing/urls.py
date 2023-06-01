from django.urls import path
from rest_framework import routers
from .views import *

router = routers.DefaultRouter()
router.register('plans', PlansViewset, basename='plans')
router.register('features', FeatureViewset, basename='features')
router.register('payment-details', PaymentDetailsViewset, basename='payment-details')
urlpatterns = [
    path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('stripe/webhook/', StripeWebhookView.as_view(), name='stripe-webhook'),
    path('remaining-disputes/<int:creator_id>/', DisputeRemainingAPI.as_view(), name='remaining-disputes')
]

urlpatterns += router.urls
