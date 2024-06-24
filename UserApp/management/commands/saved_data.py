# management/commands/sync_dynamodb.py
from django.core.management.base import BaseCommand
from UserApp.models import Sensor
import boto3

class Command(BaseCommand):
    help = 'Sync data from DynamoDB to Postgressql'

    def handle(self, *args, **kwargs):
        # Connect to DynamoDB
        dynamodb = boto3.resource('dynamodb', region_name='eu-north-1',
                                  aws_access_key_id='AKIA53CEK2BCGPA6WDO2',
                                  aws_secret_access_key='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')
        table = dynamodb.Table('cgms')

        # Fetch data from DynamoDB and insert into Django model
        response = table.scan()
        for item in response['Items']:
            # Check if a record with the same parameters (excluding sensor_id) already exists in the Sensor model
            if Sensor.objects.filter(L=item['L'], Timestamp=item['timestamp']).exists():
                # Drop the entire row if all parameters match
                continue  # Skip to the next item
            else:
                # Create Sensor object with data from DynamoDB
                Sensor.objects.create(L=item['L'], Timestamp=item['timestamp'])
                self.stdout.write(self.style.SUCCESS('New data inserted successfully'))
        
        self.stdout.write(self.style.SUCCESS('Successfully synced data from DynamoDB to local MSSQL Server'))
