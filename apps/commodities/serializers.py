from rest_framework import serializers

from apps.commodities.models import TradePartner, Commodity

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
