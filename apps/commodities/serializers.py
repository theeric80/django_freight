from rest_framework import serializers

from apps.commodities.models import TradePartner, Commodity, Inventory, InventoryHistory

class TradePartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TradePartner
        fields = ['id', 'name', 'address']

class TradePartnerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TradePartner
        fields = ['id', 'name']

class CommoditySerializer(serializers.ModelSerializer):
    class Meta:
        model = Commodity
        fields = ['id', 'name', 'description', 'trade_partner']

class CommodityListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commodity
        fields = ['id', 'name']

class InventorySerializer(serializers.ModelSerializer):
    commodity = CommoditySerializer(required=False)

    class Meta:
        model = Inventory
        fields = ['id', 'type', 'quantity', 'commodity', 'trade_partner']
        read_only_fields = ['commodity']

class InventoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = ['id', 'type', 'quantity', 'commodity', 'trade_partner']

class InventoryListSerializer(serializers.ModelSerializer):
    commodity_name = serializers.CharField(source='commodity.name')

    class Meta:
        model = Inventory
        fields = ['id', 'type', 'quantity', 'commodity_name']

class InventoryHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryHistory
        exclude = ['inventory', 'user']
