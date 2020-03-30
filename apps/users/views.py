from django.shortcuts import render

from rest_framework import generics

from apps.users.models import User
from apps.users.serializers import UserSerializer

# Create your views here.
class UserDetail(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
