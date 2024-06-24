from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.parsers import JSONParser
from django.views.decorators.csrf import csrf_exempt
from UserApp.models import Sensor, HealthData
from UserApp.serializers import SensorSerializer, HealthDataSerializer
from django.core.management import call_command
import joblib
import numpy as np
import json
import os

MODEL_FILE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'linear_regression_model.pkl'
)

LOW_THRESHOLD = 70.0
HIGH_THRESHOLD = 250.0
# Create your views here.
@csrf_exempt
def sensor_data_Api(request):
    if request.method == 'POST':
        try:
            # Call the management command
            call_command('saved_data')
            return JsonResponse({'message': 'Sync operation initiated successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        # Only allow POST method
        return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def latest_sensor_data_api(request):
    if request.method == 'GET':
        try:
            # Retrieve the latest sensor data entry
            latest_sensor_data = Sensor.objects.latest('Timestamp')

            # Serialize the sensor data
            serialized_data = {
                'L': latest_sensor_data.L,
                'timestamp': latest_sensor_data.Timestamp
            }

            # Return the serialized data as JSON response
            return JsonResponse(serialized_data, status=200)
        except Sensor.DoesNotExist:
            return JsonResponse({'error': 'No sensor data found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def healthdata_Api(request, id=0):
    if request.method == 'GET':
        health = HealthData.objects.all()
        health_serializer = HealthDataSerializer(health, many=True)
        return JsonResponse(health_serializer.data, safe=False)
    
    elif request.method == 'POST':
        health_data = JSONParser().parse(request)
        health_data_serializer = HealthDataSerializer(data=health_data)
        if health_data_serializer.is_valid():
            health_data_serializer.save()
            return JsonResponse("Added Successfully", safe=False)
        return JsonResponse(health_data_serializer.errors, status=400)

@csrf_exempt
def predict_rf(request):
    if request.method == 'POST':
        try:
            # Check if the model file exists
            if not os.path.exists(MODEL_FILE_PATH):
                raise FileNotFoundError(f"Model file not found at {MODEL_FILE_PATH}")

            # Load the model
            model = joblib.load(MODEL_FILE_PATH)

            # Check model attributes and methods
            print("Model attributes and methods:", dir(model))

            data = json.loads(request.body)

            # Extract input data
            GENDER = float(data.get('GENDER'))
            AGE = float(data.get('AGE'))
            NIR = float(data.get('NIR'))

            # Debug: Print extracted input data
            print(f"Received data - Gender: {GENDER}, Age: {AGE}, NIR: {NIR}")

            # Save input data to the database
            input_model = HealthData(
                GENDER=GENDER, AGE=AGE, NIR=NIR
            )
            input_model.save()

            # Convert input data to NumPy array
            features = np.array([GENDER, AGE, NIR]).reshape(1, -1)

            # Make prediction
            prediction = model.predict(features)
            glucose_level = prediction[0]

            # Determine status and precaution based on the predicted glucose level
            if glucose_level < LOW_THRESHOLD:
                status = "Low"
                precaution = "Take dextrose water or sugar-containing fruits."
            elif LOW_THRESHOLD <= glucose_level <= HIGH_THRESHOLD:
                status = "Normal"
                precaution = "Maintain your regular diet and activity."
            else:
                status = "High"
                precaution = "If the last insulin dose was missed, increase the dose."

            # Format the response message
            response_message = f"Your Glucose level is: {glucose_level:.2f}"

            return JsonResponse({
                'prediction': prediction.tolist(),
                'message': response_message,
                'status': status,
                'precaution': precaution
            })

        except FileNotFoundError as fnf_error:
            return JsonResponse({'error': str(fnf_error)}, status=500)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Unsupported method'}, status=405)