from django.dispatch import Signal, receiver
from django.db.models import signals

from datetime import datetime
from apps.commodities.models import Inventory, InventoryHistory

inventory_saved = Signal(providing_args=["instance", "user", "created"])
inventory_deleted = Signal(providing_args=["pk", "instance", "user"])

@receiver(inventory_saved, sender=Inventory)
def log_inventory_save(sender, instance, user, created, **kwargs):
    action = InventoryHistory.Action.ADD if created else InventoryHistory.Action.MODIFY
    detail = 'inventory (#{}) adjusted by {} (#{})'.format(instance.id, user.username, user.id)

    log = InventoryHistory(action=action, detail=detail, quantity=instance.quantity, type=instance.type, inventory=instance, user=user)
    log.save()

@receiver(inventory_deleted, sender=Inventory)
def log_inventory_delete(sender, pk, instance, user, **kwargs):
    action = InventoryHistory.Action.DELETE
    detail = 'inventory (#{}) deleted by {} (#{})'.format(pk, user.username, user.id)

    log = InventoryHistory(action=action, detail=detail, quantity=instance.quantity, type=instance.type, user=user)
    log.save()
