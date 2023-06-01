from django.db import transaction, IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import empty
from noteboard.models import Lane, Note, ProposalRelation


class LaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lane
        fields = ('id', 'name', 'display_name',)


class ProposalRelationSerializer(serializers.ModelSerializer):
    text = serializers.CharField(source='note.text', read_only=True)
    created_at = serializers.DateTimeField(source='note.created_at', read_only=True)

    class Meta:
        model = ProposalRelation
        fields = ['id', 'note', 'is_accepted', 'text', 'created_at']


class NoteSerializer(serializers.ModelSerializer):
    lane = LaneSerializer(read_only=True)
    counter_proposals = ProposalRelationSerializer(source='base_proposal', many=True)

    class Meta:
        model = Note
        fields = [
            'id', 'dispute', 'lane', 'text', 'is_caucus', 'is_strike', 'is_mediator', 'is_blur', 'is_party_attributed',
            'parent', 'created_at', 'counter_proposals']


class CounterProposalSerializer(serializers.ModelSerializer):
    base_proposal = serializers.SerializerMethodField()
    counter_proposals = serializers.SerializerMethodField(read_only=True)

    def __init__(self, instance=None, data=empty, **kwarg):
        super(CounterProposalSerializer, self).__init__(instance, data, **kwarg)
        self.lane_id = Lane.objects.get(is_proposal=True).id

    def get_base_proposal(self, obj):
        if obj.relations.base_proposal and obj.lane_id == self.lane_id:
            return obj.relations.base_proposal.id
        return None

    def get_counter_proposals(self, obj):
        if obj.relations.base_proposal and obj.lane_id == self.lane_id:
            data = Note.objects.filter(relations__base_proposal=obj.relations.base_proposal.id) \
                .values_list('id', flat=True)
            return data
        return []

    class Meta:
        model = Note
        fields = [
            'id', 'dispute', 'lane', 'text', 'is_caucus', 'is_strike', 'is_mediator', 'is_blur', 'is_party_attributed',
            'parent', 'created_at', 'base_proposal', 'counter_proposals']


class ProposalRelationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProposalRelation
        fields = ['id', 'note', 'is_accepted', 'base_proposal']


class NoteCreateSerializer(serializers.ModelSerializer):
    base_proposal = serializers.SerializerMethodField()
    counter_proposals = serializers.SerializerMethodField(read_only=True)

    def __init__(self, instance=None, data=empty, **kwargs):
        super(NoteCreateSerializer, self).__init__(instance, data, **kwargs)
        self.parent_notes = self.initial_data.pop('parent', None)
        self.base_proposal = self.initial_data.pop('base_proposal', None)
        self.countered_note = self.initial_data.pop('countered_note', None)
        self.lane_id = Lane.objects.get(is_proposal=True).id

    def get_base_proposal(self, obj):
        if obj.relations.base_proposal and obj.lane_id == self.lane_id:
            return obj.relations.base_proposal.id
        return None

    def get_counter_proposals(self, obj):
        if obj.relations.base_proposal and obj.lane_id == self.lane_id:
            data = Note.objects.filter(relations__base_proposal=obj.relations.base_proposal.id) \
                .values_list('id', flat=True)
            return data
        return []

    class Meta:
        model = Note
        fields = [
            'id', 'dispute', 'lane', 'text', 'is_caucus', 'is_strike', 'is_mediator', 'is_blur', 'is_party_attributed',
            'parent', 'created_at', 'counter_proposals', 'base_proposal']

    def link_parent(self, obj: Note):
        parent_notes = self.parent_notes
        if parent_notes:
            obj.parent.set(parent_notes)
        return obj

    def update_base_proposal_status(self):
        note = Note.objects.filter(id=self.countered_note)
        if note.exists():
            note.update(countered=True)
        else:
            raise ValidationError({"countered_note": ["host proposal with this Id does not exist"]})

    def create_proposal_relation(self, note: Note, create_counter=False):
        if create_counter:
            proposal = ProposalRelation.objects.get(note_id=self.base_proposal)
            if proposal.is_accepted:
                raise ValidationError(
                    detail={'proposal': ['Cannot create counter proposal once the proposal has been accepted']})
            proposal_relation = {'note': note.id, 'base_proposal': self.base_proposal}
            self.update_base_proposal_status()
        else:
            proposal_relation = {'note': note.id}
        serialized_proposal = ProposalRelationCreateSerializer(data=proposal_relation)
        serialized_proposal.is_valid(raise_exception=True)
        return serialized_proposal.save()

    def create(self, validated_data):
        try:
            with transaction.atomic():
                note = super().create(validated_data)
                updated_obj = self.link_parent(note)
                if self.base_proposal:
                    counter_proposal = self.create_proposal_relation(note, create_counter=True)
                else:
                    proposal = self.create_proposal_relation(note)
                return updated_obj
        except IntegrityError as error:
            raise ({"message": error})

    def update(self, instance, validated_data, partial=True):
        note = super().update(instance, validated_data)
        updated_obj = self.link_parent(note)
        return updated_obj
