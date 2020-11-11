import django_filters
from django.contrib.auth.models import User
from django_filters import CharFilter, DateFilter, NumberFilter
from .models import PointHistory

class UserFilter(django_filters.FilterSet):
    username = CharFilter(field_name='username', lookup_expr='icontains')
    unit = CharFilter(field_name='profile__unit__name', lookup_expr='icontains')
    job = CharFilter(field_name='careerhistory__job', lookup_expr='icontains')

    class Meta:
        model = User
        fields = []

    def __init__(self, *args, **kwargs):
       super(UserFilter, self).__init__(*args, **kwargs)
       self.filters['username'].label = "Username"
       self.filters['unit'].label="Unit"
       self.filters['job'].label="Job (Current & Previous)"

class PointHistoryFilter(django_filters.FilterSet):
    date_after = DateFilter(field_name='date', lookup_expr='gte')
    date_before = DateFilter(field_name='date', lookup_expr='lte')
    point_gte = NumberFilter(field_name='point', lookup_expr='gte')
    point_lte = NumberFilter(field_name='point', lookup_expr='lte')
    receiver = CharFilter(field_name='user__username', lookup_expr='icontains')
    writer = CharFilter(field_name='writer__username', lookup_expr='icontains')
    note = CharFilter(field_name='note', lookup_expr='icontains')

    class Meta:
        model = PointHistory
        fields = []

    def __init__(self, *args, **kwargs):
       super(PointHistoryFilter, self).__init__(*args, **kwargs)
       self.filters['date_after'].label = "Log(s) After (Date : MM/DD/YYYY)"
       self.filters['date_before'].label = "Log(s) Before (Date : MM/DD/YYYY)"
       self.filters['point_gte'].label = "Point ≥"
       self.filters['point_lte'].label = "Point ≤"
       self.filters['receiver'].label = "Receiver's Username"
       self.filters['writer'].label="Writer's Username"
       self.filters['note'].label="Note"
