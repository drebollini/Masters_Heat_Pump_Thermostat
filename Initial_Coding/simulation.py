import numpy as np
import json
import time
import pandas as pd
import matplotlib.pyplot as plt

coef_file = open("thermal_coefs.json", "r")
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
dt = 1 #interval time in seconds
h = int(n/dt) #no. of intervals

temp = np.zeros(h+1)
temp[0] = T_start
heating = np.zeros(h+1)

#differences method heat equ
def heat_equ(T, dt, k1, k2, T_out, q_in):
    return (dt*(k2*(T_out-T)+q_in)+(k1*T))/k1

for k in range(0, h):
    temp[k+1] = heat_equ(temp[k], dt, k1, k2, T_out, power*heating[k])

plt.plot(temp)
plt.ylim(18, 23)
plt.xlabel('time (sec)')
plt.ylabel('temp (deg)')
plt.show()

plt.plot(heating)
plt.show()

