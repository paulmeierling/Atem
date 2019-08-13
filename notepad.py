import pandas as pd
import numpy as np
from random import randint
import random, json
import sys, time
import requests
from app.routes_helpers import *

def post_data():
    start_time = time.time()
    end_time = time.time() + 2
    payload = {}
    while (time.time() < end_time):
        payload[time.time() - start_time] =  [random.randint(1,100),random.randint(200,500)]
        time.sleep(0.1)

    time_stamp = []
    pressure = []
    proximity = []
    for key in payload:
        values = payload[key]
        time_stamp.append(float(key))
        pressure.append(float(values[0]))
        proximity.append(float(values[1]))
    print('Time Stamp: ', time_stamp)
    print('Pressure: ', pressure)
    print('Proximity: ', proximity)
    start_breath, end_breath = get_breath_duration(time_stamp, pressure)
    actutation_time = get_actuation_time(time_stamp, proximity)
    print(start_breath)
    print(end_breath)
    

    #response = requests.put('http://127.0.0.1:5000/sensor_data/3', data=payload)
    #response = requests.put('http://flask-dev.stkbwuuwcd.us-east-1.elasticbeanstalk.com/sensor_data/1', data=payload)
    #print(response)

post_data()