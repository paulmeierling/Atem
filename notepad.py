import pandas as pd
import numpy as np
from random import randint
import random, json
import sys, time, csv
import requests
from app.routes_helpers import *


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
    response = requests.put('http://127.0.0.1:5000/sensor_data/1', data=payload)
    #response = requests.put('http://flask-dev.stkbwuuwcd.us-east-1.elasticbeanstalk.com/sensor_data/3', data=payload)
    print(response)

post_data()