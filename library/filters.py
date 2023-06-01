from django_filters.rest_framework import FilterSet, CharFilter, BaseInFilter, NumberFilter, BooleanFilter
from .models import Clause, Checklist, Folder


class NumberInFilter(BaseInFilter, NumberFilter):
    pass


class ClauseFilter(FilterSet):
    type = CharFilter(field_name='type', lookup_expr='exact')
    type__isnull = BooleanFilter(field_name='type', lookup_expr='isnull')
    firm = NumberFilter(field_name='firm', lookup_expr='exact')
    firm__in = NumberInFilter(field_name='firm', lookup_expr='in', distinct=True)
    firm__isnull = BooleanFilter(field_name='firm', lookup_expr='isnull')

    class Meta:
        model = Clause
        fields = ['type', 'firm', 'firm__in', 'type__isnull', 'firm__isnull']


class ChecklistFilter(FilterSet):
    type = CharFilter(field_name='type', lookup_expr='exact')
    type__isnull = BooleanFilter(field_name='type', lookup_expr='isnull')
    firm = NumberFilter(field_name='firm', lookup_expr='exact')
    firm__in = NumberInFilter(field_name='firm', lookup_expr='in', distinct=True)
    firm__isnull = BooleanFilter(field_name='firm', lookup_expr='isnull')
    category__isnull = BooleanFilter(field_name='category', lookup_expr='isnull')
    category_id = NumberFilter(field_name='category_id', lookup_expr='exact')

    class Meta:
        model = Checklist
        fields = ['type', 'firm', 'firm__in', 'type__isnull', 'firm__isnull', 'category__isnull']


class FolderFilter(FilterSet):
    type = CharFilter(field_name='type', lookup_expr='exact')
    type__isnull = BooleanFilter(field_name='type', lookup_expr='isnull')
    firm = NumberFilter(field_name='firm', lookup_expr='exact')
    firm__in = NumberInFilter(field_name='firm', lookup_expr='in', distinct=True)
    firm__isnull = BooleanFilter(field_name='firm', lookup_expr='isnull')

    class Meta:
        model = Folder
        fields = ['type', 'firm', 'firm__in', 'type__isnull', 'firm__isnull']
