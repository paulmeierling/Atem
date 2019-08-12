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
        payload[time.time() - start_time] =  [random.uniform(50,100),random.uniform(0,30)]
        time.sleep(0.1)


    response = requests.put('http://127.0.0.1:5000/sensor_data/999', data=payload)
    print(response)

post_data()