import os
from os import path
from docusign_esign import EnvelopesApi, EnvelopeDefinition, Signer, SignHere, Tabs, Recipients, \
    CarbonCopy, Document
from docusign_esign.client.api_client import ApiClient
import base64
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import constants
from litigation.models import Dispute
from .models import DocuSignEnvelope
from .serializers import EnvelopSerializer


class Docusign:
    def __init__(self):
        private_key = None
        api_client = ApiClient()
        api_client.set_base_path(os.environ.get('DOCUSIGN_AUTH_SERVER'))
        api_client.set_oauth_host_name(os.environ.get('DOCUSIGN_AUTH_SERVER'))
        private_key_file = path.abspath('docusign/pem_file/private.pem')

        if path.isfile(private_key_file):
            with open(private_key_file) as private_key_file:
                private_key = private_key_file.read()

        self.user_info = self.get_user_info(private_key, api_client)

    @classmethod
    def create_api_client(cls, base_path, access_token):
        api_client = ApiClient()
        api_client.host = base_path
        api_client.set_default_header(header_name="Authorization", header_value=f"Bearer {access_token}")
        return api_client

    def get_user_info(self, private_key, api_client):
        response = api_client.request_jwt_user_token(
            client_id=os.environ.get('DOCUSIGN_CLIENT_ID'),
            user_id=os.environ.get('DOCUSIGN_USER_ID'),
            oauth_host_name=os.environ.get('DOCUSIGN_AUTH_SERVER'),
            private_key_bytes=private_key,
            expires_in=4000,
            scopes=[
                "signature", "impersonation"
            ]
        )
        access_token = response.access_token
        user_info = api_client.get_user_info(access_token)
        accounts = user_info.get_accounts()
        api_account_id = accounts[0].account_id
        base_path = accounts[0].base_uri + "/restapi"
        return {"access_token": access_token, "api_account_id": api_account_id, "base_path": base_path}

    def create_envelope(self, filename: str, dispute: dict, subject: str, message: str):
        try:
            envelope_definition = EnvelopeDefinition()
            envelope_definition.email_subject = subject
            envelope_definition.email_blurb = message

            with open(filename, 'rb') as file:
                doc3_pdf_bytes = file.read()
            base64_file_content = base64.b64encode(doc3_pdf_bytes).decode("ascii")

            document = Document(
                document_base64=base64_file_content,
                name="Settlement-Agreement",
                file_extension="pdf",
                document_id="1"
            )
            envelope_definition.documents = [document]
            signer1 = Signer(
                email=dispute['respondent']['user']['email'],
                name=f"{dispute['respondent']['user']['first_name']} {dispute['respondent']['user']['last_name']}",
                recipient_id="1",
                routing_order="1"
            )
            signer2 = Signer(
                email=dispute['claimer']['user']['email'],
                name=f"{dispute['claimer']['user']['first_name']} {dispute['claimer']['user']['last_name']}",
                recipient_id="2",
                routing_order="2"
            )

            sign_here1 = SignHere(
                anchor_string="(Respondent)",
                anchor_units="pixels",
                recipient_id='1',
                anchor_y_offset="-30",
            )
            sign_here2 = SignHere(
                anchor_string="(Claimer)",
                anchor_units="pixels",
                recipient_id='2',
                anchor_y_offset="-30",
            )

            signer1.tabs = Tabs(sign_here_tabs=[sign_here1])
            signer2.tabs = Tabs(sign_here_tabs=[sign_here2])

            recipients = Recipients(signers=[signer1, signer2])
            envelope_definition.recipients = recipients
            envelope_definition.status = 'sent'

            api_client = self.create_api_client(base_path=self.user_info["base_path"],
                                                access_token=self.user_info["access_token"])
            envelopes_api = EnvelopesApi(api_client)
            results = envelopes_api.create_envelope(account_id=self.user_info["api_account_id"],
                                                    envelope_definition=envelope_definition)

            envelope_id = results.envelope_id
            serialized_envelope = EnvelopSerializer(data={'envelope_id': envelope_id, 'dispute': dispute['id']})
            serialized_envelope.is_valid(raise_exception=True)
            serialized_envelope.save()
            return {"envelope_id": envelope_id}
        except Exception as error:
            print(f"Error while sending document to sign {error}")


class HandleDocusignCallback(CreateAPIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        data = request.data
        docusign_event = data['event']
        envelope_id = data['data']['envelopeId']
        envelope_summary = data['data']['envelopeSummary']
        if docusign_event == "envelope-completed" and envelope_summary['status'] == 'completed':
            envelope_obj = DocuSignEnvelope.objects.filter(envelope_id=envelope_id).first()
            if envelope_obj:
                Dispute.objects.filter(id=envelope_obj.dispute_id).update(status=constants.RESOLVED)
        return Response(status=status.HTTP_200_OK)
