from django.shortcuts import render
from django.http import Http404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.commodities import serializers
from apps.commodities.models import TradePartner

class TradePartnerList(APIView):

    def get(self, request):
        # TODO: pagination
        partners = TradePartner.objects.all()
        serializer = serializers.TradePartnerListSerializer(partners, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = serializers.TradePartnerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TradePartnerDetail(APIView):

    def get_object(self, pk):
        try:
            return TradePartner.objects.get(pk=pk)
        except TradePartner.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        partner = self.get_object(pk)
        serializer = serializers.TradePartnerSerializer(partner)
        return Response(serializer.data)

    def put(self, request, pk):
        partner = self.get_object(pk)
        serializer = serializers.TradePartnerSerializer(partner, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        partner = self.get_object(pk)
        partner.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
