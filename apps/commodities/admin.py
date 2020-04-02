from django.contrib import admin

from apps.commodities import models

# Register your models here.
@admin.register(models.TradePartner)
class TradePartnerAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Commodity)
class CommodityAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Inventory)
class InventoryAdmin(admin.ModelAdmin):
    pass
