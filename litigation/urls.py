from django.urls import path
from rest_framework import routers
from .views import *

router = routers.DefaultRouter()
router.register('profiles', ProfileViewset, basename='profiles')
router.register('disputes', DisputeViewset, basename='disputes')
router.register('claimers', ClaimerViewset, basename='claimers')
router.register('respondents', RespondentViewset, basename='respondents')
router.register('creators', CreatorViewset, basename='creators')
router.register('witnesses', WitnessViewset, basename='witnesses')
router.register('claims', ClaimViewset, basename='claims')
router.register('evidences', EvidenceViewset, basename='evidences')
router.register('offers', OfferViewset, basename='offers')
router.register('partial-registration', PartialRegistrationViewset, basename='partial-registration')
router.register('timeline-steps', TimelineViewset, basename='timeline-steps')
router.register('address', AddressViewset, basename='address')
router.register('email-template', EmailTemplateViewset, basename='email-template')
router.register('dispute-actor-actions', DisputeActorActionsViewset, basename='dispute-actor-actions')
router.register('settlement-agreement', SettlementAgreementsViewset, basename="settlement-agreement")
urlpatterns = [
                  path('arbitrators/', Arbitrators.as_view(), name='arbitrators'),
                  path('submit-term-sheet/', SubmitTermSheet.as_view(), name='submit-term-sheet'),
                  path('actions/', ActionsView.as_view(), name='actions'),
                  path('complete-registration/', CompleteRegistration.as_view(), name="complete-registration"),
                  path('register/profile/', RegistrationView.as_view(), name="create-profile"),
                  path('assign-disputes/', AssignDisputes.as_view(), name="assign-disputes"),
              ] + router.urls
