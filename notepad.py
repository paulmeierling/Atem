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

def breath_timing(time_stamp, pressure):
    breath_start = 0
    breath_finish = 0
    breath_started = False
    breath_finished = False

    for i in range(0,len(time_stamp)):
        if breath_started == False and pressure[i] < -0.5:
            breath_start = time_stamp[i]
            breath_started = True
        if breath_started == True and pressure[i] > -0.5 and breath_finished == False:
            breath_finish = time_stamp[i]
            breath_finished = True
    return [breath_start, breath_finish]

def post_data():
    payload = {}
    with open("Test_run.csv") as sensor_csv:
        reader = csv.reader(sensor_csv, delimiter=',')
        pressures = []
        time_stamps = []
        for row in reader:
            time = float(row[1])
            pressure = float(row[3]) - 1018
            proximity = float(row[4])
            payload[time] = [pressure, proximity]

            pressures.append(pressure)
            time_stamps.append(time)
    print(pressures)
    print(time_stamps)
    print(breath_timing(time_stamps,pressures))
    print("CSV read")
    #response = requests.put('http://127.0.0.1:5000/sensor_data/1', data=payload)
    #response = requests.put('http://flask-dev.stkbwuuwcd.us-east-1.elasticbeanstalk.com/sensor_data/3', data=payload)
    #print(response)

post_data()