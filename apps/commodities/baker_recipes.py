from model_bakery.recipe import Recipe, foreign_key

from apps.commodities import models

trade_partner = Recipe(
    models.TradePartner,
    name = 'DHL'
)

commodity = Recipe(
    models.Commodity,
    name = 'Computers',
    trade_partner = foreign_key(trade_partner)
)

inventory = Recipe(
    models.Inventory,
    type = models.Inventory.Type.SHIPPING,
    quantity = 100,
    commodity = foreign_key(commodity),
    trade_partner = foreign_key(trade_partner)
)
