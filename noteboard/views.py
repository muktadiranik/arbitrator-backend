from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from noteboard.models import Lane, Note, ProposalRelation
from noteboard.serializers import LaneSerializer, NoteSerializer, NoteCreateSerializer, ProposalRelationSerializer, \
    CounterProposalSerializer
from rest_framework.decorators import action
from rest_framework import status, filters


class LaneViewset(ModelViewSet):
    serializer_class = LaneSerializer
    queryset = Lane.objects.all()


class NoteViewset(ModelViewSet):
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['lane', 'dispute']
    search_fields = ['text']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CounterProposalSerializer

        return NoteCreateSerializer

    def get_queryset(self):
        return Note.objects.filter(dispute__arbitrator__id=self.request.user.actor.id, countered=False)

    def partial_update(self, request, *args, **kwargs):
        data = self.request.data.copy()
        try:
            if 'lane' in data:
                proposal_lane_id = Lane.objects.get(is_proposal=True).id
                if data['lane'] == proposal_lane_id:
                    note_id = kwargs.get('pk')
                    note_obj = Note.objects.get(id=note_id)
                    ProposalRelation.objects.get_or_create(note_id=note_obj.id)
        except Exception as e:
            return Response(data=e.args, status=status.HTTP_400_BAD_REQUEST)
        return super(NoteViewset, self).partial_update(request, *args, **kwargs)

    @action(methods=['patch'], detail=False, url_name='approve-proposal', url_path='approve-proposal')
    def approve_proposal(self, request):
        proposal_id = request.data.get('proposal_id')
        proposal = ProposalRelation.objects.filter(note_id=proposal_id)
        if proposal:
            proposal.update(is_accepted=True)
            return Response(data=ProposalRelationSerializer(proposal[0]).data, status=status.HTTP_200_OK)
        else:
            return Response(data={"proposal": ["proposal with this id does not exist"]},
                            status=status.HTTP_404_NOT_FOUND)

    @action(methods=['get'], detail=True, url_name='proposal-history',
            url_path='proposal-history')
    def get_proposal_history(self, request, pk=None):
        proposal = Note.objects.filter(id=pk)
        if proposal.exists():
            base_proposal = Note.objects.get(id=pk)
            serialized_proposals = NoteSerializer(base_proposal)
            return Response(data=serialized_proposals.data, status=status.HTTP_200_OK)
        else:
            return Response(data={"proposal": ["proposal with this id does not exist"]},
                            status=status.HTTP_404_NOT_FOUND)
