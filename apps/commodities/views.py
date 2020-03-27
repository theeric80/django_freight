from django.shortcuts import render
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage

from rest_framework import mixins
from rest_framework import generics
from rest_framework import views
from rest_framework import viewsets
from rest_framework import status
from rest_framework import pagination
from rest_framework.response import Response

from apps.commodities import serializers
from apps.commodities.models import TradePartner, Commodity, Inventory

# Pagination
class LinkHeaderPagination(pagination.BasePagination):

    def paginate_queryset(self, queryset, request, view=None):
        page_num = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 20)

        try:
            self.page = Paginator(queryset, page_size).page(page_num)
            self.request = request
        except EmptyPage:
            raise Http404

        return self.page.object_list

    def get_paginated_response(self, data):
        return Response(data)

# Using class-based views
class TradePartnerList(views.APIView):
    queryset = TradePartner.objects.all()

    def get(self, request):
        paginator = LinkHeaderPagination()
        partners = paginator.paginate_queryset(self.queryset, request)
        serializer = serializers.TradePartnerListSerializer(partners, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = serializers.TradePartnerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TradePartnerDetail(views.APIView):
    queryset = TradePartner.objects.all()
    serializer_class = serializers.TradePartnerSerializer

    def get_object(self, pk):
        try:
            return self.queryset.get(pk=pk)
        except TradePartner.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        partner = self.get_object(pk)
        serializer = self.serializer_class(partner)
        return Response(serializer.data)

    def put(self, request, pk):
        partner = self.get_object(pk)
        serializer = self.serializer_class(partner, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        partner = self.get_object(pk)
        partner.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Using generic class-based views
class CommodityList(mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    generics.GenericAPIView):
    queryset = Commodity.objects.all()

    def get_serializer_class(self):
        if self.request.method.lower() == 'get':
            return serializers.CommodityListSerializer
        else:
            return serializers.CommoditySerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class CommodityDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Commodity.objects.all()
    serializer_class = serializers.CommoditySerializer

# Using ViewSets
class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = serializers.InventorySerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.InventoryListSerializer
        elif self.action == 'create':
            return serializers.InventoryCreateSerializer
        else:
            return self.serializer_class
