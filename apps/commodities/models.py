from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
class TradePartner(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=512, default='', blank=True)

    class Meta:
        db_table = 'commodities_trade_partner'
        ordering = ['id']

class Commodity(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=512, default='', blank=True)
    trade_partner = models.ForeignKey(TradePartner, null=True, on_delete=models.SET_NULL)
    class Meta:
        db_table = 'commodities_commodity'
        ordering = ['id']

class Inventory(models.Model):

    class Type(models.IntegerChoices):
        SHIPPING = 1
        RECEIVING = 2

    type = models.IntegerField(choices=Type.choices)
    quantity =  models.PositiveIntegerField()
    commodity = models.ForeignKey(Commodity, on_delete=models.CASCADE)
    trade_partner = models.ForeignKey(TradePartner, null=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'commodities_inventory'
        ordering = ['id']

class InventoryHistory(models.Model):

    class Action(models.TextChoices):
        ADD = 'a'
        MODIFY = 'm'
        DELETE = 'd'

    action = models.CharField(choices=Action.choices, max_length=2)
    detail = models.CharField(max_length=512, default='', blank=True)
    type = models.IntegerField(choices=Inventory.Type.choices)
    quantity =  models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    inventory = models.ForeignKey(Inventory, null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(get_user_model(), null=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'commodities_inventory_history'
        ordering = ['id']
