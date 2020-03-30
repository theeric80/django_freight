from django.dispatch import receiver
from django.db.models import signals

from datetime import datetime
from apps.commodities.models import Inventory, InventoryHistory


@receiver(signals.post_save, sender=Inventory)
def log_inventory_save(sender, instance, created, **kwargs):
    action = InventoryHistory.Action.ADD if created else InventoryHistory.Action.MODIFY
    detail = 'inventory (#{}) adjusted'.format(instance.id)

    log = InventoryHistory(action=action, detail=detail, quantity=instance.quantity, type=instance.type, inventory=instance)
    log.save()

@receiver(signals.post_delete, sender=Inventory)
def log_inventory_delete(sender, instance, **kwargs):
    action = InventoryHistory.Action.DELETE
    detail = 'inventory (#{}) deleted'.format(instance.id)

    log = InventoryHistory(action=action, detail=detail, quantity=instance.quantity, type=instance.type)
    log.save()
