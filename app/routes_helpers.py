from app import app, db, s3
from flask import render_template, request, redirect, url_for
from app.models import Sensor_data    
from config import Config
import os, csv, random, datetime
import boto3
import numpy as np
from itertools import compress
import pandas as pd

def smooth_data(data, size):
    return pd.DataFrame(data).iloc[:,0].rolling(size).mean()

#Returns the time when the actuation occurred based on the max gradient of proximity (may be off by 1 )
def get_actuation_time(time_stamp, proximity):
    #TO DO account for multiple actuations by looking at differentials that meet threshold?
    proximity_diff = np.diff(proximity) / np.diff(time_stamp)
    return time_stamp[np.argmax(proximity_diff)]

#Calculates breath flow rate based on pressure reading
def calculate_flow_rate(time_stamp, pressure):
    # Regression model: v = (1.51735241) * P + (-1529.15048679)
    flows = [((P*1.51735241)+(-1529.15048679))*60 for P in pressure] # (L/min)
    return flows

#Determines all the times that the user is breathing in 
def get_breathe_in(pressure, size):
    # Compute moving average on pressure data
    pressure_rolling = smooth_data(pressure, size)

    # Take pressure differential and isolate inspiration times
    pressure_diff = np.diff(pressure_rolling) / np.diff(time_stamp)
    inflow = [1 if i<=-0.75 else 0 for i in pressure_diff]
    condensed_inflow = [0 for i in range(len(inflow))]
    last = None
    for i, val in enumerate(inflow):
        if val == 1 and last == None:
            last = i # last time of inspiration
        elif val == 1:
            if abs(i-last) <= 15:
                for j in range(last,i+1):
                    condensed_inflow[j] = 1
            last = i
    return condensed_inflow, start, stop


    #    # less than 15 positives in a row (~0.25 s) false positive 
    #    #last = None
    #    for i, val in enumerate(condensed_inflow):
    #        if val == 1 and last == None:
    #            last = val # last time without inspiration
    #        elif val == 0 and last != None:
    #            if abs(i-last) <= 20:
    #                print('Current: ', i, ' Last: ', last)

    #                for j in range(last,i):
    #                    condensed_inflow[j] = 0
    #            last = None
    #return condensed_inflow    

#Calculates the start and end of longest breath
def get_breath_duration(pressure, size):
    condensed_inflow = get_breathe_in(time_stamp, pressure, size)
    last = None
    longest_stretch = None
    for i, val in condensed_inflow:
        if val == 1 and (last == None or last == 0):
            last = val
        elif val == 0 and last != None:
            if abs(last-(i-1)) > abs(longest_stretch[0]-longest_stretch[1]):
                longest_stretch = (last,i-1)
                last = i
        # ending on inflow breath
        elif val == 1 and i == len(condensed_inflow):
            if abs(last-i) > abs(longest_stretch[0]-longest_stretch[1]):
                longest_stretch = (last,i-1)
    return longest_stretch




        

