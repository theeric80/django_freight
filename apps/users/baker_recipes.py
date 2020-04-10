from model_bakery.recipe import Recipe, foreign_key

from apps.users import models

user = Recipe(
    models.User,
    username = 'lauren'
)
