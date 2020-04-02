from django.urls import path, include

from rest_framework.authtoken import views as authtoken_views

from apps.users import views


urlpatterns = [
    path('auth/token/', authtoken_views.obtain_auth_token),
    path('users/<int:pk>/', views.UserDetail.as_view()),
]
