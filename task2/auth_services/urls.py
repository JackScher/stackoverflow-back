from django.urls import path, include

from auth_services.views import GoogleLogin

urlpatterns = [
    path('accounts/', include('allauth.urls')),
    path('google/', GoogleLogin.as_view(), name='google_login')
]
