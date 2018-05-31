from django.db import models

# Create your models here.

class Fake(models.Model):

  params = models.TextField(null=True)


class Natural(models.Model):

  params = models.TextField(null=True)
