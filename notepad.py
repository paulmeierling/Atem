import pandas as pd
import numpy as np
from random import randint
import random, json
import sys, time, csv
import requests
from app.routes_helpers import *

def post_data():
    payload = {}
    with open("sample_sensor_readings.csv") as sensor_csv:
        reader = csv.reader(sensor_csv, delimiter=',')
        for row in reader:
            time = float(row[0])
            pressure = float(row[1])
            proximity = float(row[2])
            payload[time] = [pressure, proximity]

    response = requests.put('http://127.0.0.1:5000/sensor_data/4', data=payload)
    #response = requests.put('http://flask-dev.stkbwuuwcd.us-east-1.elasticbeanstalk.com/sensor_data/3', data=payload)
    print(response)

post_data()