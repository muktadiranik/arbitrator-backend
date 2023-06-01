import json
import os
import uuid
from pathlib import Path
from actstream import action as actstream
import weasyprint
from actstream.models import Follow
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.core.exceptions import PermissionDenied
from django.core.files import File as file
from django.db.models import F
from django.template import Template, Context
from django.template.loader import render_to_string
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.generics import CreateAPIView, UpdateAPIView, ListAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from library.models import Folder, File
from pricing.models import CreatorDisputeCount
from .models import Creator
from .permissions import IsSuperAdminOrRetrieve, IsCreator
from .serializers import *
from .tasks import notify_actor, send_contract, send_mail_to_superuser, on_offer_status_changed


class RegistrationView(CreateAPIView):
    helper = Helpers()
    serializer_class = RegistrationSerializer
    fake = Faker()
    parser_classes = [MultiPartParser]

    def create(self, request, *args, **kwargs):
        user = self.pop_data(request.data, 'user')
        user.update({'username': self.fake.name().replace(' ', '')})
        address = self.pop_data(request.data, 'address')
        serializer = self.get_serializer(data=request.data)
        if request.data['type'] == 'arbitrator':
            if request.user.is_superuser:
                self.perform_create(user, address, serializer, create_arbitrator=True)
            else:
                raise ValidationError(
                    {'permission_error': ['you dont have enough permissions to create an arbitrator account']})
        else:
            self.perform_create(user, address, serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update_request_data(self, dictionary):
        self.request.data._mutable = True
        self.request.data.update(dictionary)
        self.request.data._mutable = False

    def create_arbitrator(self, user, serializer):
        user['password'] = make_password(user['password'])
        serialized_user = UserSerializer(data=user)
        serialized_user.is_valid(raise_exception=True)
        auth_user = serialized_user.save()
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['user_id'] = auth_user.id
        actor = serializer.save()
        return actor

    def create_sub_agreements_folders(self, folder, actor, arbitrator: bool = False):
        folder_objects = []
        if arbitrator:
            folder_objects.append(
                Folder(arbitrator_id=actor.id, name=constants.SUB_AGREEMENT_ARBITRATOR, parent_id=folder.id,
                       relation=constants.CHILD_FOLDER, sequence=0))
        else:
            folder_objects.append(Folder(creator_id=actor.id, name=constants.SUB_AGREEMENT_CREATOR, parent_id=folder.id,
                                         relation=constants.CHILD_FOLDER, sequence=0))
        folder = Folder.objects.bulk_create(folder_objects)

    def create_agreements_folder(self, actor, arbitrator: bool = False):
        if arbitrator:
            folder, created = Folder.objects.get_or_create(arbitrator_id=actor.id, name=constants.AGREEMENT_FOLDER_NAME,
                                                           relation=constants.ROOT_FOLDER, sequence=0)
        else:
            folder, created = Folder.objects.get_or_create(creator_id=actor.id, name=constants.AGREEMENT_FOLDER_NAME,
                                                           relation=constants.ROOT_FOLDER, sequence=0)
        if created:
            self.create_sub_agreements_folders(folder, actor, arbitrator)

    def perform_create(self, user, address, serializer, create_arbitrator=False):
        try:
            with transaction.atomic():
                if create_arbitrator:
                    actor = self.create_arbitrator(user, serializer)
                    self.create_agreements_folder(actor, arbitrator=True)
                else:
                    self.update_user(user)
                    serializer.is_valid(raise_exception=True)
                    actor = serializer.save()
                    self.create_agreements_folder(actor)
                self.helper.add_user_to_actor_group(actor.user, actor.type)
                self.create_address(address, actor)
        except IntegrityError as error:
            raise APIException({"message": error})

    def post(self, request, *args, **kwargs):
        self.update_request_data({"user_id": request.user.id})
        response = super(RegistrationView, self).post(request, *args, **kwargs)
        return response

    def pop_data(self, dictionary, key):
        data = dictionary.get(key)
        data = json.loads(data)
        return data

    def update_user(self, user):
        auth_model = get_user_model()
        user_instance = auth_model.objects.get(id=self.request.user.id)
        serialized_user = UserProfileCreationSerializer(user_instance, data=user)
        serialized_user.is_valid(raise_exception=True)
        auth_user = serialized_user.save()

    def create_address(self, address, actor):
        address.update({"user": actor.id})
        serialized_address = AddressSerializer(data=address)
        serialized_address.is_valid(raise_exception=True)
        serialized_address.save()


class ProfileViewset(ModelViewSet):
    http_method_names = ['get', 'put', 'patch', 'delete', 'options', 'head']
    queryset = Actor.objects.all()
    serializer_class = ProfileSerializer


class DisputeViewset(ModelViewSet):
    serializer_class = DisputeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['=code', '=type', '=creator__user__email', '=creator__user__first_name',
                     '=creator__user__last_name', '=arbitrator__user__email', '=arbitrator__user__first_name',
                     '=arbitrator__user__last_name', '=claimer__user__email', '=claimer__user__first_name',
                     '=claimer__user__last_name', '=respondent__user__email', '=respondent__user__first_name',
                     '=respondent__user__last_name', '=witness__user__email', '=witness__user__first_name',
                     '=witness__user__last_name']
    filterset_fields = ['status', 'witness__id']
    permission_classes = [IsCreator]

    def get_serializer_context(self):
        return {"user": self.request.user, 'request': self.request}

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Dispute.objects.all()
        user_type = self.request.user.actor.type
        dispute_filter = {f'{user_type}__user_id': self.request.user.id, }
        return Dispute.objects.filter(**dispute_filter)

    def create_settlement_document(self, dispute: dict):
        file_path = os.path.join(settings.BASE_DIR, 'litigation', 'templates', 'contracts',
                                 'settlement_agreement.html')
        with open(file_path, 'r') as f:
            html_content = f.read()
            serialized_settlement_agreement = SettlementAgreementsSerializer(
                data={'dispute': dispute.get('id'), 'content': html_content})
            serialized_settlement_agreement.is_valid(raise_exception=True)
            serialized_settlement_agreement.save()
            f.close()

    @action(methods=['post'], detail=False, url_name='new-dispute',
            url_path=r'new-dispute')
    def create_new_dispute(self, request):
        errors = {}
        dispute_code = f'DIS{uuid.uuid4().hex[:6]}'
        try:
            with transaction.atomic():
                dispute = request.data.get('dispute')
                disputant = request.data.get('disputant')
                dispute.update({'code': dispute_code})
                serialized_dispute = DisputeSerializer(data=dispute,
                                                       context={"user": self.request.user, 'request': self.request})

                serialized_disputant = PartialRegistrationSerializer(data=disputant,
                                                                     context={'dispute_code': dispute_code})

                if not serialized_dispute.is_valid():
                    errors.update({'dispute': serialized_dispute.errors})
                if not serialized_disputant.is_valid():
                    errors.update({'disputant': serialized_disputant.errors})
                if errors:
                    return Response(
                        data=errors,
                        status=status.HTTP_400_BAD_REQUEST)
                created_dispute = DisputeSerializer(serialized_dispute.save()).data
                created_disputant = ProfileSerializer(serialized_disputant.save(),
                                                      context={'request': self.request}).data
                self.create_settlement_document(created_dispute)
                latest_dispute_created = Dispute.objects.get(id=created_dispute.get('id'))
                creator = User.objects.get(id=created_dispute.get('creator').get('user').get('id'))
                claimer = User.objects.get(id=created_disputant.get('user').get('id'))
                try:
                    for user in [creator, claimer]:
                        follow(user, latest_dispute_created)

                except Exception as e:
                    print(e)
                CreatorDisputeCount.objects.filter(creator=request.user.actor.id).update(
                    disputes_created=F('disputes_created') + 1)
                return Response(data={"dispute": created_dispute, 'disputant': created_disputant},
                                status=status.HTTP_200_OK)
        except IntegrityError as error:
            raise APIException({"message": error})

    @action(methods=['get'], detail=False, url_name='get-all-disputes',
            url_path=r'get-all-disputes')
    def get_all_disputes(self, request):
        if self.request.user.is_superuser:
            disputes = Dispute.objects.all()
            serialized_disputes = DisputeSerializer(disputes, many=True, context={'request': self.request})
            return Response(data=serialized_disputes.data, status=status.HTTP_200_OK)
        raise ValidationError({'User': ['User does not have enough permissions to list all the disputes']})

    @action(methods=['post'], detail=False, url_name='create-bulk-disputes',
            url_path=r'create-bulk-disputes', permission_classes=[IsAdminUser])
    def create_bulk_disputes(self, request):
        dispute_objects = []
        disputes_count = request.data.get('count')
        creator_id = request.data.get('creator_id')
        errors = {}
        if not disputes_count:
            errors.update({'count': ["count is necessary"]})
        if not creator_id:
            errors.update({'creator_id': ["count is necessary"]})
        if not errors:
            try:
                user = Actor.objects.get(id=creator_id).user
                for _ in range(0, disputes_count):
                    dispute_objects.append(
                        {"description": "Automated demo dispute", "start_date": datetime.date.today(),
                         "end_date": datetime.date.today(), "status": constants.WAITING_FOR_SIGNUP,
                         "code": f'DIS{uuid.uuid4().hex[:6]}',
                         "type": constants.HEARING})
                serialized_disputes = DisputeSerializer(data=dispute_objects, many=True, context={'user': user})
                serialized_disputes.is_valid(raise_exception=True)
                for item in serialized_disputes.validated_data:
                    item['creator_id'] = creator_id
                with transaction.atomic():
                    try:
                        disputes = serialized_disputes.save()
                    except IntegrityError as error:
                        return Response(data={'error': 'An unexpected error occurred while creating disputes.'},
                                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                serialized_disputes = DisputeSerializer(disputes, many=True)
                return Response(data=serialized_disputes.data, status=status.HTTP_200_OK)
            except Exception as e:
                return Response(data={'error': 'An unexpected error occurred.'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        raise ValidationError(errors)


class ClaimerViewset(ModelViewSet):
    http_method_names = ['get', 'patch', 'delete', 'options', 'head']
    permission_classes = [IsSuperAdminOrRetrieve]
    serializer_class = ClaimerSerializer
    queryset = Claimer.objects.all()


class RespondentViewset(ModelViewSet):
    http_method_names = ['get', 'patch', 'delete', 'options', 'head']
    permission_classes = [IsSuperAdminOrRetrieve]
    serializer_class = RespondentSerializer
    queryset = Respondent.objects.all()


class CreatorViewset(ModelViewSet):
    http_method_names = ['get', 'patch', 'delete', 'options', 'head']
    permission_classes = [IsSuperAdminOrRetrieve]
    serializer_class = CreatorSerializer
    queryset = Creator.objects.all()


class Arbitrators(ListAPIView):
    serializer_class = ArbitratorSerializer
    queryset = Arbitrator.objects.all()

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Arbitrator.objects.all()
        raise PermissionDenied()


class AssignDisputes(CreateAPIView):

    def are_all_disputes_present(self, dispute_ids: [], disputes: [Dispute]):
        return disputes.count() == len(dispute_ids)

    def validate(self, request):
        if not request.user.is_superuser:
            raise PermissionDenied("User do not have permission to perform this action.")
        required_keys = ['arbitrator_id', 'disputes']
        missing_keys = [key for key in required_keys if key not in request.data]

        if missing_keys:
            error_dict = {key: ['required field is missing'] for key in missing_keys}
            raise ValidationError(error_dict)
        arbitrator = Arbitrator.objects.filter(id=request.data['arbitrator_id']).first()
        if not arbitrator:
            raise ValidationError({"arbitrator": ['arbitrator is not present in the system']})

        disputes = Dispute.objects.filter(id__in=request.data['disputes'])

        if not self.are_all_disputes_present(request.data['disputes'], disputes):
            raise ValidationError({'dispute': ['some disputes are not present in the system']})

        dispute_approve_action = Actions.objects.filter(action__name=constants.APPROVAL_ACTION,
                                                        value=constants.DISPUTE_USER_ACTION_PENDING).first()
        if not dispute_approve_action:
            raise ValidationError({'action': ['action is not present in the system']})

        return disputes, arbitrator, dispute_approve_action

    def post(self, request, *args, **kwargs):
        disputes, arbitrator, dispute_approve_action = self.validate(self.request)

        for dispute in disputes:
            dispute_action = DisputeActorActions.objects.create(dispute_id=dispute.id, actor_id=arbitrator.id)
            dispute_action.action.add(dispute_approve_action)
        return Response(data={'message': 'disputes has been successfully assigned to the arbitrator'},
                        status=status.HTTP_200_OK)


class SubmitTermSheet(CreateAPIView):

    def create_context_dictionary(self, dispute: Dispute):
        if dispute.claimer and dispute.respondent:
            context = {
                'respondent_name': f'{dispute.respondent.user.get_full_name()}',
                'claimer_name': f'{dispute.claimer.user.get_full_name()}',
                'dispute_code': dispute.code,
                'termsheet': dispute.termsheet_set.first()
            }
            return context
        raise ValidationError({'actor': ['actor does not exist.']})

    def upload_in_document_manager(self, file_name: str):
        agreement_folder = Folder.objects.filter(arbitrator_id=self.request.user.actor.id,
                                                 name=constants.SUB_AGREEMENT_ARBITRATOR).first()
        if agreement_folder:
            path = Path(file_name)
            with path.open(mode="rb") as f:
                obj = File(folder_id=agreement_folder.id, sequence=0)
                obj.file = file(f, name=f'{path.name}')
                obj.save()
            os.remove(file_name)
            return path.name
        return None

    def post(self, request, *args, **kwargs):
        dispute_code = request.data['dispute_code']
        if not request.user.actor.type == constants.ARBITRATOR:
            raise ValidationError({"user": "the user cannot submit the termsheet"})
        arbitrator = Arbitrator.objects.get(id=request.user.actor.id)
        assigned_disputes = arbitrator.disputes_assigned.all().values_list('code', flat=True)
        if dispute_code not in list(assigned_disputes):
            raise ValidationError({"arbitrator": ["arbitrator cannot perform this action"]})
        dispute = Dispute.objects.get(code=dispute_code)
        context = self.create_context_dictionary(dispute)
        html_message = render_to_string('contracts/term-sheet.html', context)
        output_path = os.path.join(settings.MEDIA_ROOT,
                                   f'{dispute.code}_{uuid.uuid4().hex[:3]}_term_sheet.pdf')
        weasyprint.HTML(string=html_message).write_pdf(output_path)
        file_location = self.upload_in_document_manager(output_path)
        if file_location:
            task_id = send_contract.apply_async(countdown=2, kwargs={'dispute': DisputeSerializer(dispute).data,
                                                                     'subject': f'{dispute.code} Term sheet',
                                                                     'message': f"Term sheet for dispute {dispute.code}",
                                                                     'file_location': file_location})
            return Response(data={'message': "Term sheet sent successfully.", "task_id": task_id.id},
                            status=status.HTTP_200_OK)
        else:
            raise ValidationError({'file': f"cannot upload file to {constants.SUB_AGREEMENT_ARBITRATOR} folder"})


class WitnessViewset(ModelViewSet):
    http_method_names = ['get', 'patch', 'delete', 'options', 'head']
    serializer_class = WitnessSerializer
    queryset = Witness.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('disputes_witnessed__claim', 'creator__id')

    def update(self, request, *args, **kwargs):
        user = request.data.pop('user', None)
        response = super(WitnessViewset, self).update(request, *args, **kwargs)
        if user:
            try:
                user_instance = get_user_model().objects.get(id=user['id'])
            except ObjectDoesNotExist:
                raise ValidationError({'user': ["user with this id does not exist"]})
            update_user = UserSerializer(user_instance, data=user, partial=True)
            update_user.is_valid(raise_exception=True)
            update_user = update_user.save()
            response.data['user'] = UserSerializer(update_user).data
        return response

    def destroy(self, request, *args, **kwargs):
        witness = self.get_object()
        self.perform_destroy(witness.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class PartialRegistrationViewset(ModelViewSet):
    http_method_names = ['post']
    serializer_class = PartialRegistrationSerializer
    queryset = User.objects.all()

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        if self.action == 'get_actor_with_uuid':
            self.http_method_names.append('get')

    def get_serializer_context(self):
        return {"user": self.request.user}

    @action(methods=['get'], detail=False, url_name='get-actor',
            url_path=r'get-actor/(?P<unique_key>[^/.]+)', permission_classes=[AllowAny])
    def get_actor_with_uuid(self, request, unique_key=None):
        try:
            uuid_obj = UUID.objects.get(id=unique_key)
            actor_obj = uuid_obj.actor.user
            actor_data = UserSerializer(actor_obj).data
            serialized_dispute = DisputeSerializer(uuid_obj.dispute, context={'request': self.request})
            actor_data.update(
                {'creator': uuid_obj.actor.creator.id if uuid_obj.actor.type == constants.WITNESS else None,
                 'type': uuid_obj.actor.type, 'dispute': serialized_dispute.data})
            self.http_method_names.pop(1)
            return Response(data=actor_data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist as e:
            self.http_method_names.pop(1)
            return Response(data={"user": ["actor with UUID does not exist"]}, status=status.HTTP_404_NOT_FOUND)

    @action(methods=['post'], detail=False, url_name='send-invitation',
            url_path='send/invitation')
    def send_registration_mail(self, request):
        dispute = Dispute.objects.filter(code=self.request.data['dispute_code'])
        if dispute.exists():
            try:
                context = {
                    'dispute_code': self.request.data['dispute_code'],
                    'dispute_type': self.request.data['dispute_type'],
                    'invitation_link': self.request.data['invitation_link'],
                    'creator_name': self.request.data['creator_name'],
                    'recipient_name': self.request.data['recipient']['name'],
                    'recipient_email': self.request.data['recipient']['email'],
                    'title': self.request.data['title'],
                    'subject': self.request.data['subject'],
                    'actor_type': self.request.data['actor_type'],
                    'text': self.request.data['text']}

                task_id = notify_actor.delay(context)
                return Response(data={'message': "Mail sent successfully.", "task_id": task_id.id},
                                status=status.HTTP_200_OK)
            except Exception as e:
                return Response(data={'message': f'key {e} is missing'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            raise ValidationError({'dispute': ["dispute with the code doesn't exist."]})


class CompleteRegistration(UpdateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_from_request(self, data, key):
        key = data.get(key)
        return json.loads(key)

    def update_user(self, user, uuid):
        auth_model = get_user_model()
        user_instance = auth_model.objects.get(actor__uuid=uuid)
        user = user.copy()
        user.update({
            "is_active": True,
            "password": make_password(user['password'])})
        serialized_user = CompleteRegistrationSerializer(user_instance, data=user)
        serialized_user.is_valid(raise_exception=True)
        return serialized_user.save()

    def create_address(self, address, user_id):
        address.update({'user': user_id})
        serialized_address = AddressSerializer(data=address)
        serialized_address.is_valid(raise_exception=True)
        return serialized_address.save()

    def update_actor(self, actor, uuid):
        actor_instance = Actor.objects.get(uuid__id=uuid)
        serialized_actor = RegistrationSerializer(actor_instance, data=actor)
        serialized_actor.is_valid(raise_exception=True)
        return serialized_actor.save()

    def delete_handoff_template(self, actor: Actor):
        actor.email_template.all().delete()

    def update_invitation_status(self, actor):
        actor_filter = {f'{actor.type}__user__email': actor.user.email}
        disputes = Dispute.objects.filter(**actor_filter).all()
        for dispute in disputes:
            if actor.type == constants.CLAIMER:
                dispute.claimer_invitation_status = constants.INVITATION_STATUS_SIGNED
                dispute.save()
            elif actor.type == constants.RESPONDENT:
                dispute.respondent_invitation_status = constants.INVITATION_STATUS_SIGNED
                dispute.save()
        self.delete_handoff_template(actor)
        return disputes

    def perform_login(self, request, user):
        email = user['email']
        password = user['password']
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return True

        return False

    def patch(self, request, *args, **kwargs):
        data = request.data.copy()
        unique_id = data.get('uuid')
        try:
            uuid = UUID.objects.get(id=unique_id)
        except:
            return Response(data={"UUID": ["UUID is not present in the system"]}, status=status.HTTP_404_NOT_FOUND)

        user = self.get_from_request(data, 'user')
        updated_user = self.update_user(user, uuid.id)

        actor_details = self.get_from_request(data, 'actor')
        actor_details.update({"display_picture": data.get('display_picture')})
        updated_actor = self.update_actor(actor_details, uuid.id)
        serialized_actor = ProfileSerializer(updated_actor, context={'request': self.request})
        address_details = self.get_from_request(data, 'address')
        created_address = self.create_address(address_details, updated_actor.id)

        disputes = self.update_invitation_status(updated_actor)

        uuid.delete()

        user_creds = {'email': updated_user.email, 'password': user['password']}
        login_status = self.perform_login(request, user_creds)

        if login_status:
            return Response(
                data={"message": "User updated and logged in successfully.", "user": serialized_actor.data},
                status=status.HTTP_200_OK)

        return Response(data={"message": "User updated successfully but cannot log in."},
                        status=status.HTTP_400_BAD_REQUEST)


class ClaimViewset(ModelViewSet):
    serializer_class = ClaimSerializer
    queryset = Claim.objects.all()

    def get_queryset(self):
        user_type = self.request.user.actor.type
        claim_filter = {f'dispute__{user_type}__user_id': self.request.user.id}
        return Claim.objects.filter(**claim_filter)

    def get_assigned_dispute(self):

        dispute_id = self.request.data.get('dispute_id')
        try:
            return Dispute.objects.get(id=dispute_id)
        except ObjectDoesNotExist:
            raise ValidationError({'dispute': ["dispute with this id does not exist"]})

    def create(self, request, *args, **kwargs):
        related_dispute = self.get_assigned_dispute()
        request.data.update({'dispute': related_dispute.id})
        claim = super(ClaimViewset, self).create(request, args, kwargs)
        return claim


class EvidenceViewset(ModelViewSet):
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('claim_id', 'creator__id',)

    def list(self, request, *args, **kwargs):
        try:
            response = super().list(request, *args, **kwargs)
            return response
        except FileNotFoundError as error:
            raise ValidationError({'file': f'{error.filename.split("/")[-1]} does not exist in database'})

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Evidence.objects.all()
        user_type = self.request.user.actor.type
        evidence_filter = {f'claim__dispute__{user_type}__user_id': self.request.user.id}
        return Evidence.objects.filter(**evidence_filter)

    def get_actor(self, email):
        try:
            actor = Actor.objects.get(user__email=email)
            return actor
        except ObjectDoesNotExist:
            raise ValidationError({'profile': 'profile with this email does not exist'})

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return GetEvidenceSerializer
        return EvidenceSerializer

    def fetch_claim(self):
        try:
            claim_id = self.request.data.get('claim_id')
            claim = Claim.objects.get(id=claim_id)
            return claim
        except ObjectDoesNotExist:
            raise ValidationError({'claim': ["claim with the id does not exist"]})

    def fetch_dispute(self, email):
        actor_type = self.get_actor(email).type
        actor_filter = {f'{actor_type}__user__email': email}
        dispute = Dispute.objects.get(**actor_filter)
        return dispute

    def create(self, request, *args, **kwargs):
        claim = self.fetch_claim()
        actor = self.get_actor(request.data.get('user_email'))
        self.request.data.update({"claim": claim.pk, 'creator': actor.id})
        return super(EvidenceViewset, self).create(request, args, kwargs)

    def update(self, request, *args, **kwargs):
        claim = self.fetch_claim()
        actor = self.get_actor(request.data.get('user_email'))
        request.data.update({"claim": claim.pk, 'creator': actor.id})
        return super(EvidenceViewset, self).update(request, args, kwargs)

    @action(methods=['get'], detail=False, url_name='get-all-disputes',
            url_path=r'get-all-evidences')
    def get_all_evidences(self, request):
        if self.request.user.is_superuser:
            try:
                evidences = Evidence.objects.all()
                serialized_evidences = GetEvidenceSerializer(evidences, many=True, context={'request': self.request})
                return Response(data=serialized_evidences.data, status=status.HTTP_200_OK)
            except FileNotFoundError as error:
                raise ValidationError({'file': f'{error.filename.split("/")[-1]} does not exist in database'})

        raise ValidationError({'User': ['User does not have enough permissions to list all the disputes']})


class OfferViewset(ModelViewSet):
    serializer_class = OfferSerializer
    queryset = Offer.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('claim_id', 'creator__id',)

    def send_mails(self, claim):
        claim = Claim.objects.get(id=claim)
        if claim:
            superuser_email_task_id = send_mail_to_superuser.delay(mail_subject="Offer sent.",
                                                                   message=f"Respondent({claim.dispute.respondent.user.get_full_name()}) has sent the offer to claimer({claim.dispute.claimer.user.get_full_name()}) against the dispute {claim.dispute.code}")
            print(f'Offer created mail to superuser task Id: {superuser_email_task_id}')
            claimer_email_task_id = on_offer_status_changed.delay([claim.dispute.claimer.user.email],
                                                                  "Offer Received",
                                                                  f"Congratulations you got an offer against the dispute "
                                                                  f"{claim.dispute.code} from {claim.dispute.respondent.user.get_full_name()}")
            print(f'Offer received mail to claimer task Id: {claimer_email_task_id}')

    @staticmethod
    def create_notifiactions(offer: Offer):
        followers = Follow.objects.filter(object_id=offer.claim.dispute.id)
        for follower in followers:
            actstream.send(follower.user, verb=offer.status, target=offer.claim.dispute, sent=False, read=False)

    def create(self, request, *args, **kwargs):
        request.data.update({'creator': request.user.actor.id})
        response = super(OfferViewset, self).create(request, args, kwargs)
        self.send_mails(response.data.get('claim'))
        offer_id = response.data.get('id')
        offer = Offer.objects.get(id=offer_id)
        OfferViewset.create_notifiactions(offer)
        return response

    def create_context_dictionary(self, offer: Offer):
        context = {
            'dispute': offer.claim.dispute,
            'offer': offer
        }
        return context

    def upload_in_document_manager(self, file_name: str, offer: Offer):
        agreement_folder = Folder.objects.filter(creator_id=offer.claim.dispute.creator.id,
                                                 name=constants.SUB_AGREEMENT_CREATOR).first()
        if agreement_folder:
            path = Path(file_name)
            with path.open(mode="rb") as f:
                obj = File(folder_id=agreement_folder.id, sequence=0)
                obj.file.save(f'{path.name}', f, save=True)  # Use `save()` method to save the file
            os.remove(file_name)
            return path.name
        os.remove(file_name)
        return None

    def complete_timeline_steps(self, dispute):
        timeline_steps = Timeline.objects.filter(dispute_id=dispute.id, completed=False).order_by('deadline_date')
        if timeline_steps.exists():
            last_step = timeline_steps.last()
            timeline_steps.exclude(id=last_step.id).update(end_date=datetime.datetime.now(), completed=True)

    def update(self, request, *args, **kwargs):
        updated_offer = super().update(request, *args, **kwargs)
        offer = Offer.objects.filter(id=updated_offer.data.get('id')).first()
        if offer and offer.status == constants.ACCEPTED:
            self.complete_timeline_steps(offer.claim.dispute)
            context = self.create_context_dictionary(offer)
            document_content = SettlementAgreements.objects.get(dispute_id=offer.claim.dispute.id).content
            template = Template(document_content)
            html_message = template.render(Context(context))

            output_path = os.path.join(settings.MEDIA_ROOT,
                                       f'{offer.claim.dispute.code}_{uuid.uuid4().hex[:3]}_settlement.pdf')
            weasyprint.HTML(string=html_message).write_pdf(output_path)
            file_location = self.upload_in_document_manager(output_path, offer)
            if file_location:
                task_id = send_contract.apply_async(countdown=8,
                                                    kwargs={'dispute': DisputeSerializer(offer.claim.dispute).data,
                                                            'message': "Please sign the settlement agreement",
                                                            'subject': 'Agreement settlement Email',
                                                            'file_location': file_location})

            else:
                raise ValidationError({'file': f"cannot upload file to {constants.SUB_AGREEMENT_CREATOR} folder"})
        elif offer and offer.status == constants.REJECTED:
            superuser_email_task_id = send_mail_to_superuser.delay(mail_subject="Offer status changed.",
                                                                   message=f"Tha offer against against the dispute {offer.claim.dispute} has "
                                                                           f"been {constants.REJECTED} by "
                                                                           f"{offer.claim.dispute.claimer.user.get_full_name()}")
            print(f'Offer rejection mail to superuser task Id: {superuser_email_task_id}')
            respondent_email_task_id = on_offer_status_changed.delay([offer.claim.dispute.respondent.user.email],
                                                                     "Offer Rejected",
                                                                     f"{offer.claim.dispute.claimer.user.get_full_name()} has "
                                                                     f"rejected your offer against the dispute "
                                                                     f"{offer.claim.dispute.code}")
            print(f'Offer rejection mail to respondent task Id: {respondent_email_task_id}')

        OfferViewset.create_notifiactions(offer)
        return updated_offer


class TimelineViewset(ModelViewSet):
    http_method_names = ['get', 'patch']
    serializer_class = TimelineSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('dispute_id',)

    def get_queryset(self):
        user_has_actor = hasattr(self.request.user, 'actor')
        if user_has_actor:
            user_type = self.request.user.actor.type
            timeline_filter = {f'dispute__{user_type}__user_id': self.request.user.id}
            return Timeline.objects.filter(**timeline_filter).order_by('deadline_date')
        raise APIException(detail={'actor': 'actor against the user does not exist'})


class AddressViewset(ModelViewSet):
    serializer_class = AddressSerializer
    http_method_names = ['get', 'patch', 'delete']

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user.actor)


class ActionsView(ListAPIView):
    serializer_class = ActionsSerializer
    queryset = Actions.objects.all()


class DisputeActorActionsViewset(ModelViewSet):
    http_method_names = ['post', 'get']
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['actor__type', 'actor_id', 'action__action__name', 'action__value', 'dispute_id']
    queryset = DisputeActorActions.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return GetDisputeActorActionsSerializer
        return DisputeActorActionsSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        actor_id = data.get('actor')
        actions_id = data.get('action')
        actor = Actor.objects.filter(id=actor_id).first()
        actor_action = Actions.objects.filter(id__in=actions_id).first()
        if actor and actor_action:
            if actor.type == constants.ARBITRATOR and actor_action.action.name == constants.APPROVAL_ACTION and \
                    actor_action.value == constants.DISPUTE_USER_ACTION_ACCEPTED:
                dispute = Dispute.objects.filter(id=data.get('dispute'))
                if dispute.exists():
                    dispute = dispute.first()
                    dispute.arbitrator_id = actor_id
                    dispute.save()
        else:
            raise ValidationError({"data": ["actor or action With these Ids are not present"]})

        return super().create(request, args, kwargs)

    def get_rejected_actions(self):
        rejected_action = DisputeActorActions.objects.filter(
            action__action__name=constants.APPROVAL_ACTION,
            action__value=constants.DISPUTE_USER_ACTION_REJECTED,
            actor_id=self.request.user.actor.id
        )
        if rejected_action.exists():
            return rejected_action
        return None

    @action(methods=['get'], detail=False, url_name='unassigned-disputes',
            url_path=r'unassigned-disputes')
    def get_unassigned_disputes(self, request):
        if request.query_params:
            query_params = self.request.query_params
            action_name = query_params.get('action__action__name')
            action_value = query_params.get('action__value')

            if (action_value and action_value == constants.DISPUTE_USER_ACTION_PENDING) and (
                    action_name and action_name == constants.APPROVAL_ACTION):
                self.rejected_actions = self.get_rejected_actions()

        dispute_ids = self.filter_queryset(
            DisputeActorActions.objects.filter(actor__user__id=request.user.id).values_list(
                'dispute',
                flat=True))

        if hasattr(self, 'rejected_actions') and self.rejected_actions:
            for rejected_action in self.rejected_actions:
                if rejected_action.dispute_id in list(dispute_ids):
                    dispute_ids = dispute_ids.exclude(dispute_id=rejected_action.dispute_id)
        if dispute_ids:
            disputes = Dispute.objects.filter(id__in=dispute_ids, arbitrator__user_id=None)

            serialized_disputes = DisputeSerializer(disputes, many=True).data
            return Response(data=serialized_disputes, status=status.HTTP_200_OK)
        else:
            return Response(data=[],
                            status=status.HTTP_200_OK)


class EmailTemplateViewset(ModelViewSet):
    http_method_names = ['get', 'post', 'patch']
    serializer_class = EmailTemplateSerializer
    queryset = EmailTemplate.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['actor_id', 'dispute_id']

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        data = response.data
        dispute_object = Dispute.objects.get(id=data['dispute'])
        actor_type = data.get('actor_type')
        if actor_type and actor_type == constants.CLAIMER:
            dispute_object.claimer_invitation_status = constants.INVITATION_STATUS_DRAFT
            dispute_object.save()
        elif actor_type and actor_type == constants.RESPONDENT:
            dispute_object.respondent_invitation_status = constants.INVITATION_STATUS_DRAFT
            dispute_object.save()
        return response


class SettlementAgreementsViewset(ModelViewSet):
    http_method_names = ['get', 'patch']
    serializer_class = SettlementAgreementsSerializer
    queryset = SettlementAgreements.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['dispute_id']
