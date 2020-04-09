from django.shortcuts import render
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage
from django.db import transaction
from django.db.models import F, Q, Sum, Case, When, Value
from django.db.models.functions import Coalesce

from rest_framework import mixins
from rest_framework import generics
from rest_framework import views
from rest_framework import viewsets
from rest_framework import status
from rest_framework import pagination
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.decorators import action
from rest_framework.utils.urls import replace_query_param

from apps.commodities import serializers
from apps.commodities import signals
from apps.commodities.models import TradePartner, Commodity, Inventory, InventoryHistory

import logging

logger = logging.getLogger(__name__)


# Pagination
class LinkHeaderPagination(pagination.BasePagination):
    page_size = api_settings.PAGE_SIZE
    page_query_param = 'page'
    page_size_query_param = 'page_size'

    def paginate_queryset(self, queryset, request, view=None):
        page_num = request.GET.get(self.page_query_param, 1)
        page_size = request.GET.get(self.page_size_query_param, self.page_size) or 30

        try:
            self.page = Paginator(queryset, page_size).page(page_num)
            self.request = request
        except EmptyPage:
            raise Http404

        return self.page.object_list

    def get_paginated_response(self, data):
        headers = {
            'Link': self._get_link_header()
        }
        return Response(data, headers=headers)

    def _get_link_header(self):
        links = []
        links.append(self.get_next_link())
        links.append(self.get_last_link())
        links.append(self.get_first_link())
        links.append(self.get_prev_link())

        return ', '.join(filter(lambda x: bool(x), links))

    def get_next_link(self):
        if not self.page.has_next():
            return None

        page_num = self.page.next_page_number()
        page_size = self.page.paginator.per_page
        return self.get_link(page_num, page_size, 'next')

    def get_prev_link(self):
        if not self.page.has_previous():
            return None

        page_num = self.page.previous_page_number()
        page_size = self.page.paginator.per_page
        return self.get_link(page_num, page_size, 'prev')

    def get_first_link(self):
        first_page_num = 1
        if self.page.number <= first_page_num: # is_first_page
            return None

        page_size = self.page.paginator.per_page
        return self.get_link(first_page_num, page_size, 'first')

    def get_last_link(self):
        last_page_num = self.page.paginator.num_pages
        if self.page.number >= last_page_num: # is_last_page
            return None

        page_size = self.page.paginator.per_page
        return self.get_link(last_page_num, page_size, 'last')

    def get_link(self, page, size, rel):
        replaced_uri = self.request.build_absolute_uri()
        replaced_uri = replace_query_param(replaced_uri, self.page_query_param, page)
        replaced_uri = replace_query_param(replaced_uri, self.page_size_query_param, size)
        return '<{}>; rel="{}"'.format(replaced_uri, rel)

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

    @transaction.atomic
    def perform_create(self, serializer):
        instance = serializer.save()
        user = self.request.user

        # TODO: replace custom signal with explicit function call
        # https://docs.djangoproject.com/en/3.0/topics/signals/#defining-and-sending-signals
        signals.inventory_saved.send(sender=Inventory, instance=instance, user=user, created=True)

    @transaction.atomic
    def perform_update(self, serializer):
        instance = serializer.save()
        user = self.request.user
        signals.inventory_saved.send(sender=Inventory, instance=instance, user=user, created=False)

    def perform_destroy(self, instance):
        pk=instance.id
        user = self.request.user

        with transaction.atomic():
            instance.delete()
            signals.inventory_deleted.send(sender=Inventory, pk=pk, instance=instance, user=user)

    @action(detail=False, methods=['get'])
    def summary(self, request, *args, **kwargs):
        """
        SELECT
          "commodities_inventory"."commodity_id",
          "commodities_commodity"."name" AS "commodity_name",
          COALESCE(SUM("commodities_inventory"."quantity"), 0) AS "total_quantity",
          COALESCE(SUM(CASE
            WHEN "commodities_inventory"."type" = 1 THEN "commodities_inventory"."quantity"
            ELSE 0
          END), 0) AS "shipping_quantity",
          COALESCE(SUM(CASE
            WHEN "commodities_inventory"."type" = 2 THEN "commodities_inventory"."quantity"
            ELSE NULL
          END), 0) AS "receiving_quantity"
        FROM "commodities_inventory"
        INNER JOIN "commodities_commodity"
          ON ("commodities_inventory"."commodity_id" = "commodities_commodity"."id")
        GROUP BY "commodities_inventory"."commodity_id",
                 "commodities_commodity"."name",
                 "commodities_commodity"."id"
        ORDER BY "commodities_commodity"."id" ASC
        """
        queryset = Inventory.objects.values('commodity') \
            .annotate(commodity_name = F('commodity__name')) \
            .annotate(total_quantity = Coalesce(Sum(F('quantity')),  Value(0))) \
            .annotate(shipping_quantity = Coalesce(Sum(Case(When(type=Inventory.Type.SHIPPING, then=F('quantity')), default=0)), Value(0))) \
            .annotate(receiving_quantity = Coalesce(Sum(F('quantity'), filter=Q(type=Inventory.Type.RECEIVING)), Value(0))) \
            .order_by('commodity')

        logger.debug(queryset.query)

        instance = self.paginate_queryset(queryset)
        serializer = serializers.InventorySummarySerializer(instance, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['get'])
    def history(self, request, *args, **kwargs):
        queryset = InventoryHistory.objects.all()
        instance = self.paginate_queryset(queryset)
        serializer = serializers.InventoryHistorySerializer(instance, many=True)
        return self.get_paginated_response(serializer.data)
