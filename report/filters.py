import django_filters
from .models import Tag
from django_filters import CharFilter

class TagFilter(django_filters.FilterSet):
    name = CharFilter(field_name='name', lookup_expr='icontains')
    description = CharFilter(field_name='description', lookup_expr='icontains')
    creator = CharFilter(field_name='creator__username', lookup_expr='icontains')

    class Meta:
        model = Tag
        fields = []

    def __init__(self, *args, **kwargs):
       super(TagFilter, self).__init__(*args, **kwargs)
       self.filters['name'].label = "Name"
       self.filters['description'].label="Description"
       self.filters['creator'].label="Creator"
