"""TA URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as authview
from django.urls import path, include
from report import views as reportview
from user import views as userview
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', reportview.SubscribedReportListView.as_view(), name='home'),
    path('about/', reportview.About, name='about'),
    path('dashboard/', reportview.Dashboard, name='dashboard'),

    path('login/', authview.LoginView.as_view(template_name='user/login.html'), name='login'),
    path('logout/', authview.LogoutView.as_view(template_name='user/logout.html'), name='logout'),
    path('password-reset/', authview.PasswordResetView.as_view(template_name='user/password_reset.html'), name='password_reset'),
    path('password-reset/done/', authview.PasswordResetDoneView.as_view(template_name='user/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', authview.PasswordResetConfirmView.as_view(template_name='user/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', authview.PasswordResetCompleteView.as_view(template_name='user/password_reset_complete.html'),name='password_reset_complete'),

    path('register/', userview.register, name='register'),
    path('profile/', userview.profile, name='profile'),

    path('report-new', reportview.ReportCreateView.as_view(), name='report-create'),
    path('report/all', reportview.ReportListView.as_view(), name='all-reports'),
    path('report/<int:pk>/', reportview.ReportDetailView.as_view(), name='report-detail'),
    path('report/<int:pk>/update/', reportview.ReportUpdateView.as_view(), name='report-update'),
    path('report/<int:pk>/delete/', reportview.ReportDeleteView.as_view(), name='report-delete'),

    path('tag/<str:tagname>', reportview.TagReportListView.as_view(), name='tag-reports'),
    path('tag-new', reportview.TagCreateView.as_view(), name='tag-create'),
    path('tag-list', reportview.TagList, name='tag-list'),

    path('progress-taken', reportview.ProgressTaken, name='progress-taken'),
    path('progress-subscribed', reportview.ProgressSubscribed, name='progress-subscribed'),

    path('unit-new/', userview.UnitCreateView.as_view(), name='unit-create'),
    path('unit/<int:pk>', userview.UnitDetail, name='unit-detail'),
    path('unit-hierarchy', userview.UnitHierarchy, name='unit-list'),

    path('user/<str:username>', reportview.UserReportListView.as_view(), name='user-reports'),
    path('user/<str:username>/taken', reportview.UserTakenListView.as_view(), name='user-taken'),
    path('user/<str:username>/collaboration', reportview.UserCollaborationListView.as_view(), name='user-collab'),
    path('user/<str:username>/career', reportview.UserCareerListView.as_view(), name='user-career'),
    path('user/<str:username>/point', reportview.UserPointListView.as_view(), name='user-point'),
    # path('user/<str:username>/training', views.UserTrainingListView.as_view(), name='user-training'),
    path('user-list', userview.UserList, name='user-list'),

    path('auth', userview.AuthDetail, name='auth-detail'),

    path('point-new/', userview.PointHistoryCreateView.as_view(), name='point-create'),
    path('point-list/', userview.PointHistoryList, name='point-list'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
