from django.urls import path, include

from apps.users import views


urlpatterns = [
    path('users/<int:pk>/', views.UserDetail.as_view()),
]
