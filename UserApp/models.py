from django.db import models

# Create your models here.
class Sensor(models.Model):
  
    L = models.CharField(max_length=50)
    Timestamp = models.CharField(max_length=50)

class HealthData(models.Model):
    
    GENDER = models.CharField(max_length=50, null=True)
    AGE = models.CharField(max_length=50, null=True)
    NIR  = models.CharField(max_length=50, null=True)
    