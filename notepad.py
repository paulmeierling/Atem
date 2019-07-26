import pandas as pd
import requests
import json
from random import randint
import random
import sys
import time


winning_chance = 5/38

for i in range (1,1000):
    previous_bet = 2
    current_bet = 2
    total_payment = 0
    winnings = 0
    net_cash = 0
    while(current_bet < 200000000):
        total_payment = total_payment + current_bet
        gamble = random.random()
        if(gamble > winning_chance):
            winnings = current_bet*2
            net_cash = winnings - total_payment
            print("You made:", net_cash)
            break
        previous_bet = current_bet
        current_bet = current_bet*2




# #Reads a csv -> compile to Json
# #print(sys.argv[0])
# #print(sys.argv[1])
# start_time = time.time()
# end_time = time.time() + 10
# dataset = {}
# while (time.time() < end_time):
#     dataset[time.time()-start_time] = str(random.uniform(50,100)) + ";" + str(random.uniform(0,30))
#     time.sleep(0.1)

# #dataset = {0.6450842389342234: [1012.49697823789324324789, 25.56890234089234890423], 0.96757324324234324: [1012.47777887787, 25.612322323], 1.012: [1008.32423432234,25.7877777]}
# #response = requests.post('http://127.0.0.1:5000/write_sensor_data/1340', data=dataset)
# #response = requests.post('http://flask-dev.stkbwuuwcd.us-east-1.elasticbeanstalk.com/write_sensor_data/4', data=dataset)
# #print(response.content)
# print("done")