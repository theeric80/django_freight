from django.db import models

# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'users_user'
