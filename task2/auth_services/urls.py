from django.urls import path, include
# from auth_services.views import CustomLoginView
from auth_services.views import CustomGoogleAuthView

urlpatterns = [
    path('accounts/', include('allauth.urls')),
    # path('accounts/google/login/callback/', include('allauth.urls')),
    path('google/<str:key>', CustomGoogleAuthView.as_view()),
]
