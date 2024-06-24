from django.urls import path
from django.http import HttpResponse
from UserApp import views


def home(request):
    return HttpResponse("Hello World")

urlpatterns = [
path('',home),
path('sensordata/',views.sensor_data_Api),
path('latestsensordata/',views.latest_sensor_data_api),
path('healthdata/',views.healthdata_Api),
 path('predictglucose/', views.predict_rf, name='predict_rf'),

]