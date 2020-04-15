from django.db import models
from django.db.models import F, Q, Sum, Case, When, Value as V
from django.db.models.functions import Coalesce
from django.contrib.auth import get_user_model


# Create your managers here.
class InventoryQuerySet(models.QuerySet):

    def shipping(self):
        return self.filter(type__exact=Inventory.Type.SHIPPING)

    def receiving(self):
        return self.filter(type__exact=Inventory.Type.RECEIVING)

class InventoryManager(models.Manager):

    def summarize(self):
        SHIPPING = Inventory.Type.SHIPPING
        RECEIVING = Inventory.Type.RECEIVING

        return self.values('commodity') \
            .annotate(commodity_name = F('commodity__name')) \
            .annotate(total_quantity = Coalesce(Sum('quantity'),  V(0))) \
            .annotate(shipping_quantity = Coalesce(Sum(Case(When(type=SHIPPING, then=F('quantity')), default=0)), V(0))) \
            .annotate(receiving_quantity = Coalesce(Sum('quantity', filter=Q(type=RECEIVING)), V(0))) \
            .order_by()

    def list_glutted_commodities(self, quantity):
        return self.values('commodity') \
            .annotate(total_quantity = Coalesce(Sum('quantity'), V(0))) \
            .filter(total_quantity__gte=quantity) \
            .order_by('-total_quantity')


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
    objects = InventoryManager.from_queryset(InventoryQuerySet)()

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
    inventory = models.ForeignKey(Inventory, db_index=False, null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(get_user_model(), null=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'commodities_inventory_history'
        ordering = ['id']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['inventory', 'created_at']),
        ]
