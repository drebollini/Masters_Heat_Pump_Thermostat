import numpy as np
import json
import time
import pandas as pd
import matplotlib.pyplot as plt
plt.style.use('seaborn-poster')

coef_file = open("themal_coefs.json", "r")
coef_JSON = coef_file.read()
coef_file.close()
coef = json.loads(coef_JSON)


#constants
power = coef['q_in'] #heater power/W
T_out = 9.5 #degrees C outside on the night of 1st-2nd December 2022 London City Airport
T_start = 22.18 #starting temperature indoors - from import data
k1 = coef['k1']
k2 = coef['k2']

#Thermostat
thermostat_target = 21.5
thermostat_range = 0.5
thermostat_target_max = thermostat_target + thermostat_range/2
thermostat_target_min = thermostat_target - thermostat_range/2
minimum_time_on = 60*15 #minimum time on in seconds

#boundaries
n = 24*60*60 #24 hours in sec
dt = 1 #interval time in seconds
h = int(n/dt) #no. of intervals

#heat ODE
def heat_ODE(T, k1, k2, T_out, q_in):
    return (1/k1)*(k2*(T-T_out)+q_in)
    
#differences method heat equ
def heat_equ(T, dt, k1, k2, T_out, q_in):
    return (dt*(k2*(T_out-T)+q_in)+(k1*T))/k1

#Bang-bang algorithm
temp = np.zeros(h+1)
temp[0] = T_start
heating = np.zeros(h+1)
heating_track = 0
for k in range(0, h):
    temp[k+1] = heat_equ(temp[k], dt, k1, k2, T_out, power*heating[k])
    if temp[k] < thermostat_target_min:
        heating[k+1] = 1
        heating_track = 1
    if temp[k] > thermostat_target_min:
        if heating_track == 1:
            heating[k+1] = 1
        if heating_track == 0:
            heating[k+1] = 0
    if temp[k] > thermostat_target_max:
        heating[k+1] = 0
        heating_track = 0

plt.plot(temp)
plt.ylim(18, 23)
xlim = np.arange(0, 60*60*28, 60*60*4)
plt.xticks(xlim, ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'])
plt.xlabel('time')
plt.ylabel('temp (deg C)')
plt.show()

plt.plot(heating)
xlim = np.arange(0, 60*60*28, 60*60*4)
plt.xticks(xlim, ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'])
plt.xlabel('time (sec)')
plt.ylabel('power (bool)')
plt.show()