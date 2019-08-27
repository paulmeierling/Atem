import pandas as pd
import numpy as np
from random import randint
import random, json
import sys, time, csv
import requests
from app.routes_helpers import *

def calculate_flow_rate(pressure):
    # Regression model: v = -18.26216 + (36.90) * P 
    flows = [-18.26 + 36.90*(p-baseline) for p in pressure] # (L/min)
    return flows

def post_data():
    payload = {}
    with open("Test_run.csv") as sensor_csv:
        reader = csv.reader(sensor_csv, delimiter=',')
        for row in reader:
            time = float(row[1])
            pressure = float(row[3]) -  1018
            proximity = float(row[4])
            payload[time] = [pressure, proximity]
    print("CSV read")
    response = requests.put('http://127.0.0.1:5000/sensor_data/1', data=payload)
    #response = requests.put('http://flask-dev.stkbwuuwcd.us-east-1.elasticbeanstalk.com/sensor_data/3', data=payload)
    print(response)

post_data()