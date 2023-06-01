from django.contrib import admin
from .models import User, Actor, UUID, Address, Dispute, Claimer, Respondent, Claim, Offer, Evidence, Witness, \
    Arbitrator, Timeline, Actions, ActionNames, DisputeActorActions, EmailTemplate, SettlementAgreements

admin.site.register(ActionNames)
admin.site.register(Actions)


# admin.site.register(DisputeActorActions)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_filter = ['is_active', 'is_superuser']
    search_fields = ['id', 'email', 'first_name', 'last_name']
    list_display = ['email', 'first_name', 'last_name', 'is_active', 'is_superuser']


@admin.register(Dispute)
class DisputeAdmin(admin.ModelAdmin):
    search_fields = ['id', 'code', 'creator__user__email', 'arbitrator__user__email']
    list_filter = ['actions__action__action', 'actions__action__value', 'type', 'status']
    list_display = ['code', 'creator', 'status', 'arbitrator', 'type']


@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    readonly_fields = ["created_at", "signed_up_at"]
    list_filter = ['account', 'category', 'relation']
    search_fields = ['id', 'type', 'creator__user__email', 'user__email']
    list_display = ['user', 'type', 'creator', 'created_at', 'signed_up_at']


@admin.register(UUID)
class UUIDAdmin(admin.ModelAdmin):
    readonly_fields = ["id", "created_at", "max_age", "actor"]
    search_fields = ['actor__user__email', 'dispute__code']
    list_display = ['id', 'actor', 'dispute', 'created_at']


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    search_fields = ['user__user__email', 'id', 'city', 'state', 'zip']
    list_display = ['user', 'city', 'state', 'zip']


@admin.register(Arbitrator)
class ArbitratorAdmin(admin.ModelAdmin):
    readonly_fields = ["created_at", "signed_up_at"]
    list_filter = ['account', 'category', 'relation']
    search_fields = ['id', 'type', 'creator__user__email', 'user__email']
    list_display = ['user', 'type', 'creator', 'created_at', 'signed_up_at']


@admin.register(Claimer)
class ClaimerAdmin(admin.ModelAdmin):
    readonly_fields = ["created_at", "signed_up_at"]
    list_filter = ['account', 'category', 'relation']
    search_fields = ['id', 'type', 'creator__user__email', 'user__email']
    list_display = ['user', 'type', 'creator', 'created_at', 'signed_up_at']


@admin.register(Respondent)
class RespondentAdmin(admin.ModelAdmin):
    readonly_fields = ["created_at", "signed_up_at"]
    list_filter = ['account', 'category', 'relation']
    search_fields = ['id', 'type', 'creator__user__email', 'user__email']
    list_display = ['user', 'type', 'creator', 'created_at', 'signed_up_at']


@admin.register(Witness)
class WitnessAdmin(admin.ModelAdmin):
    readonly_fields = ["created_at", "signed_up_at"]
    list_filter = ['account', 'category', 'relation']
    search_fields = ['id', 'type', 'creator__user__email', 'user__email']
    list_display = ['user', 'type', 'creator', 'created_at', 'signed_up_at']


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    search_fields = ['id', 'dispute__code']
    list_display = ['dispute', 'claimed_amount', 'created_at']


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_filter = ['status']
    search_fields = ['id', 'creator__user__email' 'dispute__code']
    list_display = ['creator', 'claim', 'offered_amount', 'status', 'created_at']


@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):
    search_fields = ['id', 'creator__user__email', 'claim__dispute__code']
    list_display = ['creator', 'claim', 'created_at']


@admin.register(DisputeActorActions)
class DisputeActorActionsAdmin(admin.ModelAdmin):
    list_filter = ['action__action', 'action__value']
    search_fields = ['id', 'dispute__code', 'actor__user__email', 'action__action__name']
    list_display = ['dispute', 'action_name', 'actor', 'created_at']

    def action_name(self, obj):
        return [action.action.name for action in obj.action.all()]


@admin.register(Timeline)
class TimelineAdmin(admin.ModelAdmin):
    list_filter = ['completed', 'name']
    search_fields = ['id', 'dispute__code']
    list_display = ['dispute', 'name', 'deadline_date', 'completed']


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_filter = ['actor__type']
    search_fields = ['dispute__code']
    list_display = ['dispute']


@admin.register(SettlementAgreements)
class SettlementAgreementsAdmin(admin.ModelAdmin):
    search_fields = ['id', 'dispute__code']
    list_display = ['dispute', 'created_at']
