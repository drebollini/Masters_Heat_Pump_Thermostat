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

#boundaries
n = 24*60*60 #24 hours in sec
dt = 60 #interval time in seconds
h = int(n/dt) #no. of intervals

#Thermostat
thermostat_target = 20 #thermostat target at end of boundary

#heat ODE
def heat_ODE(T, k1, k2, T_out, q_in):
    return (1/k1)*(k2*(T-T_out)+q_in)
    
#differences method heat equ
def heat_equ(T, dt, k1, k2, T_out, q_in):
    return (dt*(k2*(T_out-T)+q_in)+(k1*T))/k1

#backwards differences method heat equ
def heat_equ_back(T, dt, k1, k2, T_out, q_in):
    return -(dt*(k2*(T_out-T)+q_in)-(k1*T))/k1

#Bang-bang algorithm
temp_heating = np.zeros(h+1)
temp_heating[-1] = thermostat_target
temp_cooling = np.zeros(h+1)
temp_cooling[0] = T_start
heating = np.zeros(h+1)
heating[:] = 1

temp_heating = np.flip(temp_heating)
for k in range(0, h):
    temp_heating[k+1] = heat_equ_back(temp_heating[k], dt, k1, k2, T_out, power*heating[k])
temp_heating = np.flip(temp_heating)

for k in range(0, h):
    temp_cooling[k+1] = heat_equ(temp_cooling[k], dt, k1, k2, T_out, 0)


for k in range(0,h):
    if temp_heating[k] < temp_cooling[k]:
        heating[k] = 0
    if temp_heating[k] > temp_cooling[k]:
        heating[k] = 1

temp = np.zeros(h+1)
temp[0] = T_start
for k in range(0, h):
    temp[k+1] = heat_equ(temp[k], dt, k1, k2, T_out, power*heating[k])

plt.plot(temp)
plt.ylim(15, 25)
plt.xlabel('time (sec)')
plt.ylabel('temp (deg)')
plt.show()

plt.plot(heating)
plt.show()