from rest_framework import serializers
from UserApp.models import  Sensor, HealthData
class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = (
            'L',
            'Timestamp',
        )

class HealthDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthData
        fields = (
            'GENDER',
            'AGE',
            'NIR',
        
        )