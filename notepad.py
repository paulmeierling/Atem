import pandas as pd
import numpy as np
from random import randint
import random, json
import sys, time
import requests

def post_data():
    start_time = time.time()
    end_time = time.time() + 2
    payload = {}
    while (time.time() < end_time):
        payload[time.time() - start_time] =  [random.randint(1,100),random.randint(200,500)]
        time.sleep(0.1)

    response = requests.put('http://127.0.0.1:5000/sensor_data/1', data=payload)
    #response = requests.put('http://flask-dev.stkbwuuwcd.us-east-1.elasticbeanstalk.com/sensor_data/1', data=payload)
    print(response)

post_data()