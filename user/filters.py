import django_filters
from django.contrib.auth.models import User
from django_filters import CharFilter

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
