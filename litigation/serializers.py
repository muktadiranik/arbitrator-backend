import datetime

from actstream.actions import follow
from allauth.utils import build_absolute_uri
from dj_rest_auth.serializers import UserDetailsSerializer
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, IntegrityError
from faker import Faker
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import empty

import constants
from core.models import User
from pricing.models import CreatorDisputeCount
from .models import Actor, Address, Dispute, Claimer, Respondent, UUID, Claim, Offer, Evidence, Witness, Timeline, \
    Actions, DisputeActorActions, ActionNames, Arbitrator, EmailTemplate, SettlementAgreements, Creator
from core.helpers import Helpers


class UUID_serializer(serializers.ModelSerializer):
    id = serializers.CharField(required=False)
    dispute = serializers.PrimaryKeyRelatedField(queryset=Dispute.objects.all(), required=False)

    class Meta:
        model = UUID
        fields = ('id', 'actor', 'dispute')


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    address = serializers.SerializerMethodField()

    def get_address(self, obj):
        addresses = obj.actor.address.all()
        if addresses:
            serialized_addresses = AddressSerializer(addresses, many=True).data
            for address in serialized_addresses:
                address.pop('user')
            return serialized_addresses
        return None

    class Meta:
        model = get_user_model()
        read_only_fields = ('id',)
        fields = ('id', 'username', 'first_name', 'last_name', 'is_active', 'email', 'password', 'address',)


class UserProfileCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name')


class RegistrationSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=False)
    user = UserSerializer(read_only=True)
    phone_number = serializers.CharField(required=False)

    class Meta:
        model = Actor
        fields = ('id', 'user_id', 'display_picture', 'user', 'account', 'type', 'category', 'company', 'phone_number',)

    def has_organization(self, account):
        if account == 'organization':
            return True
        return False

    def validate_company(self, value):
        account = self.initial_data['account']
        if self.has_organization(account) and not value:
            raise ValidationError("Company cannot be null")
        return value


class AddressSerializer(serializers.ModelSerializer):
    state = serializers.CharField(required=False)

    class Meta:
        model = Address
        fields = ('id', 'user', 'first_address', 'second_address', 'city', 'state', 'zip')


class ActorTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ['id', 'type']


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)
    phone_number = serializers.CharField(required=False)
    invitation_url = serializers.SerializerMethodField()
    creator = ActorTypeSerializer(required=False)

    def get_invitation_url(self, obj):
        try:
            path = f"/auth/signup;unique-key={obj.uuid.id}"
            url = build_absolute_uri(None, path)
        except ObjectDoesNotExist:
            path = f"/auth/login"
            url = build_absolute_uri(None, path)
        return url

    class Meta:
        model = Actor
        fields = ['id', 'display_picture', 'user', 'account', 'type', 'category', 'company', 'phone_number', 'creator',
                  'invitation_url']


class TimelineSerializer(serializers.ModelSerializer):
    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        self.current_step_decided = False

    current_step = serializers.SerializerMethodField()
    end_date = serializers.DateField(required=False)

    def get_current_step(self, obj):
        if obj.completed or self.current_step_decided:
            return False
        else:
            self.current_step_decided = not self.current_step_decided
            return True

    def update(self, instance, validated_data):
        if 'end_date' in validated_data:
            validated_data['completed'] = True
        return super(TimelineSerializer, self).update(instance, validated_data)

    class Meta:
        model = Timeline
        fields = ['id', 'dispute', 'name', 'deadline_date', 'current_step', 'end_date']
        read_only_fields = ['current_step']


class ActionNamesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActionNames
        fields = ['name']


class DisputeSerializer(serializers.ModelSerializer):
    creator = ProfileSerializer(required=False)
    claimer = ProfileSerializer(required=False)
    arbitrator = ProfileSerializer(required=False)
    respondent = ProfileSerializer(required=False)
    claimer_invitation_status = serializers.CharField(required=False)
    respondent_invitation_status = serializers.CharField(required=False)
    claim = serializers.SerializerMethodField()
    actions = serializers.SerializerMethodField(read_only=True)

    def validate(self, attrs):
        response = super().validate(attrs)
        actor = self.get_user()
        disputes_count = CreatorDisputeCount.objects.filter(creator_id=actor.id)
        if not disputes_count.exists() or disputes_count.first().disputes_created > disputes_count.first().disputes_available:
            raise ValidationError(detail={"plan": "please buy a plan to create disputes"})
        return response

    def get_actions(self, obj):
        latest_action = None
        for dispute_actor_action in obj.actions.order_by('-created_at').all()[:1]:
            for action in dispute_actor_action.action.all():
                latest_action = {
                    "name": action.action.name,
                    "value": action.value
                }
        return latest_action

    def get_claim(self, obj):
        try:
            serialized_claim = ClaimSerializer(obj.claim)
            return serialized_claim.data
        except ObjectDoesNotExist:
            return None

    class Meta:
        model = Dispute
        fields = ['id', 'description', 'created_at', 'closed_at', 'start_date', 'end_date', 'status',
                  'creator', 'arbitrator', 'claimer', 'respondent', 'actions', 'code', 'type',
                  'respondent_invitation_status', 'claimer_invitation_status', 'claim', 'contains_witness']

    def get_user(self):
        try:
            user = self.context.get('user')
            if not user:
                raise serializers.ValidationError({"user": ["user object is necessary in serializer context"]})
            actor = Actor.objects.get(user_id=user.id)
            return actor
        except ObjectDoesNotExist:
            raise serializers.ValidationError({"actor": ["profile must be created before creating a dispute"]})

    def create_timeline_steps(self, dispute_id: int):
        for index, step in enumerate(constants.TIMELINE_STEPS, 1):
            deadline_date = datetime.date.today() + datetime.timedelta(
                days=constants.STEPS_DIFFERENCE * index)
            step_data = {"dispute": dispute_id, 'name': step,
                         'deadline_date': deadline_date}
            serialized_steps = TimelineSerializer(data=step_data)
            serialized_steps.is_valid(raise_exception=True)
            serialized_steps.save()

    def create(self, validated_data):
        validated_data['creator_id'] = self.get_user().id
        try:
            with transaction.atomic():
                response = super(DisputeSerializer, self).create(validated_data)
                self.create_timeline_steps(response.id)
                return response
        except IntegrityError as error:
            raise serializers.ValidationError(error)


class NestedDisputeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dispute
        fields = ['id', 'code']


class ClaimerSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    invitation_url = serializers.SerializerMethodField()
    disputes = NestedDisputeSerializer(source='disputes_claimed.all', many=True, read_only=True)

    def get_invitation_url(self, obj):
        try:
            path = f"/auth/signup;unique-key={obj.uuid.id}"
            url = build_absolute_uri(None, path)
        except ObjectDoesNotExist:
            path = f"/auth/login"
            url = build_absolute_uri(None, path)
        return url

    class Meta:
        model = Claimer
        fields = ("id", 'user', "account", 'disputes', "type", "category", "company", "phone_number", "created_at",
                  "signed_up_at",
                  'invitation_url',)


class RespondentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    invitation_url = serializers.SerializerMethodField()
    disputes = NestedDisputeSerializer(source='disputes_responded.all', many=True, read_only=True)

    def get_invitation_url(self, obj):
        try:
            path = f"/auth/signup;unique-key={obj.uuid.id}"
            url = build_absolute_uri(None, path)
        except ObjectDoesNotExist:
            path = f"/auth/login"
            url = build_absolute_uri(None, path)
        return url

    class Meta:
        model = Respondent
        fields = ("id", 'user', "account", "type", "disputes", "category", "company", "phone_number", "created_at",
                  "signed_up_at", 'invitation_url',)


class CreatorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    disputes = NestedDisputeSerializer(source='disputes.all', many=True, read_only=True)

    class Meta:
        model = Creator
        fields = ("id", 'user', "account", "type", "disputes", "category", "company", "phone_number", "created_at",
                  "signed_up_at",)


class ArbitratorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    disputes = NestedDisputeSerializer(source='disputes_assigned.all', many=True, read_only=True)

    class Meta:
        model = Arbitrator
        fields = ["id", 'user', "account", "type", 'disputes', "category", "company", "phone_number", "created_at",
                  "signed_up_at"]


class WitnessSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    invitation_url = serializers.SerializerMethodField()
    creator = ActorTypeSerializer(read_only=True)
    disputes = serializers.SerializerMethodField(read_only=True)

    def get_disputes(self, obj):
        return obj.disputes_witnessed.through.objects.filter(witness_id=obj.id).values_list('dispute_id', flat=True)

    def get_invitation_url(self, obj):
        try:
            path = f"/auth/signup;unique-key={obj.uuid.id}"
            url = build_absolute_uri(None, path)
        except ObjectDoesNotExist:
            path = f"/auth/login"
            url = build_absolute_uri(None, path)
        return url

    class Meta:
        model = Witness
        fields = ["id", 'user', "account", "type", "category", "company", "phone_number", "created_at", "signed_up_at",
                  'relation', 'creator', 'invitation_url', 'display_picture', 'disputes']
        read_only_fields = ('user', 'creator', 'invitation_url',)


class PartialRegistrationSerializer(serializers.ModelSerializer):
    helper = Helpers()
    fake = Faker()
    password = serializers.CharField(required=False)
    username = serializers.CharField(required=False)
    user = UserSerializer(required=False)
    dispute = DisputeSerializer(required=False)
    invitation_url = serializers.SerializerMethodField()
    relation = serializers.CharField(required=False)
    creator = ActorTypeSerializer(required=False)

    def get_invitation_url(self, obj):
        try:
            path = f"/auth/signup;unique-key={obj.uuid.id}"
            url = build_absolute_uri(None, path)
            return url
        except ObjectDoesNotExist:
            path = f"/auth/login"
            url = build_absolute_uri(None, path)
            return url

    class Meta:
        model = Actor
        fields = (
            'id', 'user', 'type', 'phone_number', 'password', 'username', 'invitation_url', 'dispute', 'relation',
            'creator', 'created_at', 'signed_up_at', 'account', 'company')

    def __init__(self, instance=None, data=empty, **kwargs):
        super(PartialRegistrationSerializer, self).__init__(instance, data, **kwargs)
        try:
            self.auth_user_data = self.initial_data.pop('user')
            self.auth_user_data.update({'email': self.auth_user_data['email'].lower()})
            self.dispute = self.initial_data.pop('dispute') if 'dispute' in self.initial_data else {
                "code": self.context.get('dispute_code')}
        except:
            pass

    def get_user_data(self):
        data = self.auth_user_data
        username = self.fake.name().replace(' ', '')
        data.update({'is_active': False, 'username': username})
        return data

    def update_status_to_signed(self, actor, dispute):
        dispute = dispute.first()
        if actor.type == constants.CLAIMER:
            dispute.claimer_invitation_status = constants.INVITATION_STATUS_SIGNED
        elif actor.type == constants.RESPONDENT:
            dispute.respondent_invitation_status = constants.INVITATION_STATUS_SIGNED
        dispute.save()

    def update_dispute_object(self, actor, created=True):
        dispute = self.dispute
        dispute = Dispute.objects.filter(code=dispute['code'])
        if dispute:
            dispute_id = dispute[0].id
            if actor.type == constants.CLAIMER:
                dispute[0].claimer_id = actor.id
            elif actor.type == constants.RESPONDENT:
                follow(actor.user, dispute[0])
                dispute[0].respondent_id = actor.id
            elif actor.type == constants.ARBITRATOR:
                dispute[0].arbitrator_id = actor.id
            else:
                witness = Witness.objects.get(id=actor.id)
                dispute[0].witness.add(witness)
                dispute[0].contains_witness = True
            dispute[0].save()
            if not created and (actor.type == 'claimer' or actor.type == 'respondent') and actor.user.is_active:
                self.update_status_to_signed(actor, dispute)
            return dispute_id
        else:
            raise serializers.ValidationError({'dispute': ['dispute with the code does not exist']})

    def create_UUID(self, actor, dispute_id):
        data = {'actor': actor.id, 'dispute': dispute_id}
        serialized_uuid = UUID_serializer(data=data)
        serialized_uuid.is_valid(raise_exception=True)
        uuid_obj = serialized_uuid.save()
        return uuid_obj

    def is_witness(self):
        if self.initial_data.get('type') == 'witness':
            return True
        return False

    def validate(self, attrs):
        errors = {}
        account = attrs.get('account')
        if account and account == constants.ORGANIZATION:
            company = attrs.get('company')
            if not company:
                raise ValidationError({"company": ["company is necessary for organization account"]})
        user_data = self.get_user_data()
        user = get_user_model().objects.filter(email=user_data['email'])
        if user.exists():
            requested_type = self.initial_data.get("type")
            saved_role = user[0].actor.type
            if saved_role != requested_type:
                errors.update({'user': [
                    f'user cannot be registered as {self.initial_data.get("type")} because it has already '
                    f'been registered as {user[0].actor.type}']})
        if errors:
            raise serializers.ValidationError(errors)
        else:
            return attrs

    def get_session_user(self):
        user = self.context.get('user')
        return user

    def create_user(self):
        user_data = self.get_user_data()
        user = User.objects.filter(email=user_data['email'])
        if user.exists():
            if user.first().actor.type == constants.WITNESS:
                raise ValidationError({"witness": ["witness with this email already exists"]})
            return user[0], False
        else:
            serializer = UserSerializer(data=user_data)
            serializer.is_valid(raise_exception=True)
            auth_user = serializer.save()
            return auth_user, True

    def create(self, validated_data):
        try:
            with transaction.atomic():
                auth_user, created = self.create_user()
                validated_data['user'] = auth_user
                if created:
                    actor = super().create(validated_data)
                if self.is_witness():
                    user = self.get_session_user()
                    auth_user.actor.creator_id = user.actor.id
                    auth_user.actor.save()
                dispute_id = self.update_dispute_object(auth_user.actor, created)
                if created:
                    self.create_UUID(actor, dispute_id)
                    self.helper.add_user_to_actor_group(auth_user, auth_user.actor.type)
                return auth_user.actor
        except IntegrityError as error:
            raise serializers.ValidationError(error)


class CustomUserDetailsSerializer(UserDetailsSerializer):
    actor = serializers.SerializerMethodField()
    disputes = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        actor = Actor.objects.filter(user_id=instance.id)
        self.user_actor = actor.first() if actor.exists() else None

    def get_actor(self, obj):
        if self.user_actor:
            return ProfileSerializer(self.user_actor, context=self.context).data
        else:
            raise ValidationError({'actor': []})

    def get_disputes(self, obj):
        if self.user_actor:
            match obj.actor.type:
                case constants.CLAIMER:
                    return obj.actor.disputes_claimed.all().values_list('id', flat=True)
                case constants.ARBITRATOR:
                    return obj.actor.disputes_assigned.all().values_list('id', flat=True)
                case constants.RESPONDENT:
                    return obj.actor.disputes_responded.all().values_list('id', flat=True)
                case constants.WITNESS:
                    witness = Witness.objects.get(id=obj.actor.id)
                    return witness.disputes_witnessed.all().values_list('id', flat=True)
                case _:
                    return obj.actor.disputes.all().values_list('id', flat=True)
        else:
            raise ValidationError({'actor': []})

    def get_permissions(self, obj):
        perms = sorted(obj.get_all_permissions())
        return perms

    class Meta(UserDetailsSerializer.Meta):
        fields = UserDetailsSerializer.Meta.extra_fields + ['permissions', 'disputes', 'actor', 'is_superuser']


class CompleteRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email', 'password', 'is_active']


class OfferSerializer(serializers.ModelSerializer):
    claim = serializers.PrimaryKeyRelatedField(required=False, queryset=Claim.objects.all())
    creator = serializers.PrimaryKeyRelatedField(required=False, queryset=Actor.objects.all())
    claimed_amount = serializers.SerializerMethodField()

    def get_claimed_amount(self, obj):
        return obj.claim.claimed_amount

    class Meta:
        model = Offer
        fields = ['id', 'offered_amount', 'currency', 'status', 'creator', 'created_at', 'updated_at',
                  'claimed_amount', 'claim', 'offer_accepted_modal_rendered', 'offer_received_modal_rendered']
        read_ony_fields = ('id', 'updated_at', 'created_at',)

    def validate(self, attrs):
        response = super().validate(attrs)
        claim = self.initial_data.get('claim')
        pending_offer = Offer.objects.filter(claim=claim, status=constants.PENDING)
        if pending_offer.exists():
            raise ValidationError({'offer': ['An offer already pending on the claim']})
        return response


class ClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model = Claim
        fields = ['id', 'dispute', 'description', 'created_at', 'updated_at', 'claimed_amount']


class EvidenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evidence
        fields = ['id', 'claim', 'attachment', 'creator', 'created_at', 'extension', 'size']
        read_only_fields = ('created_at', 'extension', 'size')


class GetEvidenceSerializer(serializers.ModelSerializer):
    creator = ActorTypeSerializer()
    dispute = serializers.IntegerField(source='claim.dispute.id', read_only=True)

    class Meta:
        model = Evidence
        fields = ['id', 'claim', 'dispute', 'attachment', 'creator', 'created_at', 'extension', 'size']
        read_only_fields = ('created_at', 'extension', 'size')


class ActionsSerializer(serializers.ModelSerializer):
    action = ActionNamesSerializer(read_only=True)

    class Meta:
        model = Actions
        fields = ['id', 'action', 'value']


class DisputeActorActionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisputeActorActions
        fields = ['id', 'dispute', 'actor', 'action', 'created_at', 'updated_at']

    def validate(self, data):
        response = super().validate(data)
        dispute = data.get('dispute')
        actor = data.get('actor')
        action = data.get('action')[0]

        actor_actions = self.Meta.model.objects.filter(dispute=dispute, actor=actor, action=action)
        if not actor_actions.exists():
            return response
        else:
            raise serializers.ValidationError({"non_field_errors": [
                f"{actor.user.first_name} {actor.user.last_name} has already performed {action.action.name} on dispute {dispute.code}"
            ]})


class GetDisputeActorActionsSerializer(serializers.ModelSerializer):
    actor = ProfileSerializer()

    class Meta:
        model = DisputeActorActions
        fields = ['id', 'dispute', 'action', 'actor', 'created_at', 'updated_at']


class EmailTemplateSerializer(serializers.ModelSerializer):
    invitation_link = serializers.SerializerMethodField()
    actor_type = serializers.CharField(source='actor.type', read_only=True, required=False)
    actor = serializers.PrimaryKeyRelatedField(queryset=Actor.objects.all(), write_only=True)

    class Meta:
        model = EmailTemplate
        fields = ['id', 'dispute', 'invitation_link', 'dispute_type', 'template_title', 'email_subject', 'actor_type',
                  'content', 'actor', 'creator_name', 'recipient_name', 'recipient_email']

    def get_invitation_link(self, obj):
        try:
            uuid_relation = obj.actor.uuid.id
            path = f"/auth/signup;unique-key={uuid_relation}"
            url = build_absolute_uri(None, path)
        except ObjectDoesNotExist:
            path = f"/auth/login"
            url = build_absolute_uri(None, path)
        return url


class SettlementAgreementsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SettlementAgreements
        fields = ['id', 'dispute', 'content', 'created_at', 'updated_at']
