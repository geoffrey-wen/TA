from django.urls import path
from . import views

urlpatterns = [
    path('', views.SubscribedReportListView.as_view(), name='home'),
    path('new/', views.About, name='about'),

    path('report/all', views.ReportListView.as_view(), name='all-reports'),
    path('tag/<str:tagname>', views.TagReportListView.as_view(), name='tag-reports'),

    path('user/<str:username>', views.UserReportListView.as_view(), name='user-reports'),
    path('user/<str:username>/taken', views.UserTakenListView.as_view(), name='user-taken'),
    path('user/<str:username>/collaboration', views.UserCollaborationListView.as_view(), name='user-collaboration'),
    path('user/<str:username>/career', views.UserCareerListView.as_view(), name='user-career'),
    path('user/<str:username>/point', views.UserPointListView.as_view(), name='user-point'),
    # path('user/<str:username>/training', views.UserTrainingListView.as_view(), name='user-training'),

    path('report-new', views.ReportCreateView.as_view(), name='report-create'),
    path('report/<int:pk>/', views.ReportDetailView.as_view(), name='report-detail'),
    path('report/<int:pk>/update/', views.ReportUpdateView.as_view(), name='report-update'),
    path('report/<int:pk>/delete/', views.ReportDeleteView.as_view(), name='report-delete'),

    path('tag-new', views.TagCreateView.as_view(), name='tag-create'),
    path('tag-list', views.TagList, name='tag-list'),

    path('progress-taken', views.ProgressTaken, name='progress-taken'),
    path('progress-subscribed', views.ProgressSubscribed, name='progress-subscribed'),
]
