from django.db import models

# Create your models here.
class TradePartner(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=512, default='')

    class Meta:
        db_table = 'commodities_trade_partner'

class Commodity(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=512, default='')
    trade_partner = models.ForeignKey(TradePartner, null=True, on_delete=models.SET_NULL)
    class Meta:
        db_table = 'commodities_commodity'

class Inventory(models.Model):

    class Type(models.IntegerChoices):
        SHIPPING = 1
        RECEIVING = 2

    type = models.IntegerField(choices=Type.choices)
    quantity =  models.PositiveIntegerField()
    commodity = models.ForeignKey(Commodity, null=True, on_delete=models.CASCADE)
    trade_partner = models.ForeignKey(TradePartner, null=True, on_delete=models.SET_NULL)
    class Meta:
        db_table = 'commodities_inventory'
