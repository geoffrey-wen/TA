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
from user import views as userview
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('report.urls')),

    path('login/', authview.LoginView.as_view(template_name='user/login.html'), name='login'),
    path('logout/', authview.LogoutView.as_view(template_name='user/logout.html'), name='logout'),
    path('password-reset/', authview.PasswordResetView.as_view(template_name='user/password_reset.html'), name='password_reset'),
    path('password-reset/done/', authview.PasswordResetDoneView.as_view(template_name='user/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', authview.PasswordResetConfirmView.as_view(template_name='user/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', authview.PasswordResetCompleteView.as_view(template_name='user/password_reset_complete.html'),name='password_reset_complete'),

    path('register/', userview.register, name='register'),
    path('profile/', userview.profile, name='profile'),

    path('unit-new/', userview.UnitCreateView.as_view(), name='unit-create'),
    path('unit/<int:pk>', userview.UnitDetail, name='unit-detail'),

    path('auth', userview.AuthDetail, name='auth-detail'),

    path('point-new/', userview.PointHistoryCreateView.as_view(), name='point-create'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
