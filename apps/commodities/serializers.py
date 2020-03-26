from rest_framework import serializers

from apps.commodities.models import TradePartner

class TradePartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TradePartner
        fields = ['id', 'name', 'address']

class TradePartnerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TradePartner
        fields = ['id', 'name']
