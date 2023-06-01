import json
import os

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, IntegrityError
from django.db.models import ProtectedError, F
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet
from stripe.error import InvalidRequestError

import constants
from litigation.models import Creator
from .serializers import GetPlanSerializer, CreatePlanSerializer, FeatureSerializer, PaymentDetailSerializer, \
    CreatorDisputeCountSerializer
from .models import Plan, Feature, PaymentDetail, CreatorDisputeCount
from rest_framework import permissions, status
from rest_framework.response import Response
from django.shortcuts import redirect
import stripe
from allauth.utils import build_absolute_uri
from .tasks import send_payment_details_to_creator
from litigation.permissions import IsSuperAdminOrRetrieve, IsCreator
from django.shortcuts import get_object_or_404


class PlansViewset(ModelViewSet):
    queryset = Plan.objects.all()
    stripe.api_key = os.environ.get('STRIPE_API_KEY')

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        else:
            return [permissions.IsAuthenticated(), permissions.IsAdminUser()]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return GetPlanSerializer
        return CreatePlanSerializer

    def update(self, request, *args, **kwargs):
        if 'active' in request.data and request.data.get('active') == False:
            plan = self.get_object()
            product_id = plan.stripe_product_id
            product = stripe.Product.retrieve(product_id)
            product.active = False
            product = product.save()
            response = super().update(request, *args, **kwargs)
            response.data.update({"stripe_product_status": product.get('active')})
            return response

    def destroy(self, request, *args, **kwargs):
        plan = self.get_object()
        product_id = plan.stripe_product_id
        with transaction.atomic():
            try:
                try:
                    product = stripe.Product.retrieve(product_id)
                    product.active = False
                    product = product.save()
                except InvalidRequestError as e:
                    if 'No such product' in str(e):
                        print("Product does not exist")
                    else:
                        print("Stripe error:", str(e))
                try:
                    return super().destroy(request, *args, **kwargs)
                except ProtectedError as e:
                    raise ValidationError(detail={"payment": ['payment attached to this plan']})
            except IntegrityError as error:
                raise APIException({"message": error})

    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                response = super().create(request, *args, **kwargs)
                features = Feature.objects.filter(id__in=response.data.get('feature')).values_list('text', flat=True)
                product = stripe.Product.create(
                    name=request.data.get('name'),
                    type='service',
                    description=request.data.get('description'),
                    attributes=['features_list'],
                    metadata={
                        'features_list': ', '.join(features)
                    }
                )
                Plan.objects.filter(id=response.data.get('id')).update(
                    stripe_product_id=product.id)
                price = stripe.Price.create(
                    unit_amount=int(request.data.get('price') * 100),
                    currency='usd',
                    product=product.id
                )
                response.data.update({'stripe_product_id': product.id})
        except IntegrityError as error:
            raise APIException({"message": error})

        return response


class FeatureViewset(ModelViewSet):
    serializer_class = FeatureSerializer
    queryset = Feature.objects.all()
    permission_classes = [permissions.IsAdminUser, permissions.IsAuthenticated]


class CreateCheckoutSessionView(CreateAPIView):
    permission_classes = [IsCreator]

    def create(self, request, *args, **kwargs):
        try:
            plan_id = request.data.get('plan_id')
            if not plan_id:
                raise ValidationError(detail={"plan_id": {"plan id is necessary"}})
            try:
                plan = Plan.objects.get(id=plan_id)
                success_url = build_absolute_uri(None, f'/plans/{plan.id}/checkout/success')
                cancel_url = build_absolute_uri(None, f'/plans/{plan.id}/checkout/failure')
            except ObjectDoesNotExist:
                raise ValidationError(detail={"plan": ["plan with this id does not exist"]})
            product_id = plan.stripe_product_id
            price = stripe.Price.list(product=product_id).data[0]
            with transaction.atomic():
                try:
                    payment_data = {"creator": request.user.actor.id, 'plan': plan.id}
                    serialized_payment_details = PaymentDetailSerializer(data=payment_data)
                    serialized_payment_details.is_valid(raise_exception=True)
                    payment_intent_created = serialized_payment_details.save()

                    try:
                        creator_dispute_count_object = CreatorDisputeCount.objects.get(
                            creator_id=request.user.actor.id)
                    except ObjectDoesNotExist:
                        serialized_dispute_count = CreatorDisputeCountSerializer(
                            data={'creator': request.user.actor.id, 'disputes_created': 0,
                                  'disputes_available': 0})
                        serialized_dispute_count.is_valid(raise_exception=True)
                        serialized_dispute_count.save()
                    checkout_session = stripe.checkout.Session.create(
                        line_items=[
                            {
                                'price': price.get('id'),
                                'quantity': 1,
                            },
                        ],
                        mode='payment',
                        success_url=success_url,
                        cancel_url=cancel_url,
                        payment_intent_data={
                            'metadata': {
                                'creator_id': str(request.user.actor.id),
                                'payment_intent_id': payment_intent_created.id
                            },
                        }
                    )

                    print(checkout_session.url)
                except IntegrityError as error:
                    raise APIException({"message": error})
        except Exception as e:
            return Response({'error': str(e)})
        return Response(data={"redirect_url": checkout_session.url}, status=status.HTTP_200_OK)


class StripeWebhookView(CreateAPIView):
    permission_classes = [AllowAny]
    stripe.api_key = os.environ.get('STRIPE_API_KEY')

    @csrf_exempt
    def create(self, request, *args, **kwargs):

        payload = request.body
        try:
            event = stripe.Event.construct_from(
                json.loads(payload), stripe.api_key
            )
        except ValueError as e:
            return Response(data={'error': e}, status=400)
        if event.type == 'checkout.session.expired':
            print("Checkout session failed of a user")
        session = event.data.object
        payment_intent_id = session.payment_intent
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        creator_id = payment_intent.metadata.get('creator_id')
        payment_intent_local_id = payment_intent.metadata.get('payment_intent_id')
        if creator_id and payment_intent_id:
            payment_status = payment_intent.status
            payment_id = payment_intent.id
            payment_detail = get_object_or_404(PaymentDetail, id=payment_intent_local_id)
            payment_detail.stripe_payment_status = payment_status
            payment_detail.stripe_payment_id = payment_id
            payment_detail.is_subscription_active = True
            payment_detail.save()
            creator = Creator.objects.get(id=creator_id)
            if payment_intent.status == constants.PAYMENT_STATUS_SUCCEEDED:
                CreatorDisputeCount.objects.filter(creator_id=creator.id).update(
                    disputes_available=F('disputes_available') + creator.payment_details.last().plan.disputes)
            subject = f"Payment Details - {payment_intent_id}"
            message = f"Dear {payment_detail.creator.user.get_full_name()},\n\n" \
                      f"We would like to inform you that the status of your recent payment on arbitration agreement has been updated.\n\n" \
                      f"Payment Details:\n" \
                      f"----------------------------------------\n" \
                      f"Payment Reference/ID: {payment_intent_id}\n" \
                      f"Payment Amount: {payment_intent.amount / 100}\n" \
                      f"Payment Status: {payment_status}\n" \
                      f"----------------------------------------\n\n" \
                      f"Please review the updated status of your payment. If you have any questions or concerns, feel free to contact our support team at [Contact Email/Phone].\n\n" \
                      f"Thank you for your payment and continued support.\n\n" \
                      f"Best regards,\n" \
                      f"Arbitration Agreement"
            send_payment_details_to_creator.delay(subject, message,
                                                  [payment_detail.creator.user.email])
        return Response(status=200)


class PaymentDetailsViewset(ModelViewSet):
    http_method_names = ['get', 'delete']
    serializer_class = PaymentDetailSerializer
    queryset = PaymentDetail.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('creator_id',)
    permission_classes = [IsSuperAdminOrRetrieve]


class DisputeRemainingAPI(RetrieveAPIView):
    permission_classes = [IsCreator]

    def get(self, request, *args, **kwargs):
        creator = kwargs.get('creator_id')
        creator_dispute_count = CreatorDisputeCount.objects.filter(creator_id=creator)
        if creator_dispute_count.exists():
            remaining_disputes = creator_dispute_count.first().disputes_available - \
                                 creator_dispute_count.first().disputes_created
            return Response(data={"remaining_disputes": remaining_disputes}, status=status.HTTP_200_OK)
        else:
            return Response(data={"plan": ["no plan purchased"]}, status=status.HTTP_400_BAD_REQUEST)
