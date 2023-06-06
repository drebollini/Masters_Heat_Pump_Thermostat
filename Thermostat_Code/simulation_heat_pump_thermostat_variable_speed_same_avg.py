import numpy as np
import json
import time
import pandas as pd
import matplotlib.pyplot as plt

#Read Files
inputs = pd.read_csv(r'Thermostat_Code\inputs.csv', header=None)#.to_numpy()
coef_file = open(r"Thermostat_Code\thermal_coefs.json", "r")
coef_JSON = coef_file.read()
coef_file.close()
coef = json.loads(coef_JSON)

#Simulation boundaries
n = 24*60*60*7 #24 hours, 7 days

#Simulation Constants
power = coef['q_in'] #heater power/W
T_out = 10 #degrees C outside
T_start = 18 #starting temperature indoors
k1 = coef['k1']
k2 = coef['k2']
dt = 60 #interval time in seconds
h = int(n/dt) #no. of intervals
inputs[2] = inputs[2]/dt #recalibrate inputs

#Functions
#heat ODE
def heat_ODE(T, k1, k2, T_out, q_in):
    return (1/k1)*(k2*(T-T_out)+q_in)
    
#differences method heat equ
def heat_equ(T, dt, k1, k2, T_out, q_in):
    return (dt*(k2*(T_out-T)+q_in)+(k1*T))/k1

#input target array
input_target_track=np.zeros(h+1)
input_target = 18
for l in range(0, h):
    input_target_track[l] = input_target
    if l in inputs[2].to_numpy():
        command = inputs.loc[inputs[2] == l]
        command_0 = command[0].values[0]
        command_1 = command[1].values[0]
        input_target = command_1

#Proportional Algorithm
P = 5
temp = np.zeros(h+1)
temp[0] = T_start
heating_curve = np.zeros(h+1)
heating_power = np.zeros(h+1)
heating_target = 18
heating_target_track = np.zeros(h+1)
current_command_no = 0
for k in range(0, h):
    #Simulate next state
    temp[k+1] = heat_equ(temp[k], dt, k1, k2, T_out, power*heating_power[k])
    heating_target_track[k] = heating_target

    #check for manual inputs
    if k in inputs[2].to_numpy():
        command = inputs.loc[inputs[2] == k]
        command_0 = command[0].values[0]
        command_1 = command[1].values[0]
        if command_0 == 2:
            heating_target = command_1
            current_command = ((command.index.to_numpy())[0])
        if command_0 == 1:
            heating_target = command_1
            current_command = ((command.index.to_numpy())[0])

    #achieve target tempt by time
    if (k+60*3) in inputs[2].to_numpy():
        command = inputs.loc[inputs[2] == (k+dt*3)]
        command_0 = command[0].values[0]
        command_1 = command[1].values[0]
        if command_0 == 1 and command_1 > temp[k]:
            heating_target = command_1
            current_command = ((command.index.to_numpy())[0])
    
    #auto-reduce
    if (k-60*3) in inputs[2].to_numpy():
        command = inputs.loc[inputs[2] == (k-60*3)]
        command_0 = command[0].values[0]
        command_1 = command[1].values[0]
        if command_1 > 20 and current_command_no == ((command.index.to_numpy())[0]):
            heating_target = command_1-1

    set_power = P*((heating_target-0.5)-temp[k])+0.3
    if set_power > 1:
        heating_power[k+1] = 1
    if set_power < 0:
        heating_power[k+1] = 0
    if 1 > set_power > 0:
        heating_power[k+1] = set_power

plt.plot(temp)
plt.plot(input_target_track)
plt.ylim(15, 25)
xlim = np.arange(0, n/dt, 60*60*4/dt)
plt.xticks(xlim, ['Day 1: 00:00', '04:00', '08:00', '12:00', '16:00', '20:00',
                   'Day 2: 00:00', '04:00', '08:00', '12:00', '16:00', '20:00',
                   'Day 3: 00:00', '04:00', '08:00', '12:00', '16:00', '20:00',
                   'Day 4: 00:00', '04:00', '08:00', '12:00', '16:00', '20:00',
                   'Day 5: 00:00', '04:00', '08:00', '12:00', '16:00', '20:00',
                   'Day 6: 00:00', '04:00', '08:00', '12:00', '16:00', '20:00',
                   'Day 7: 00:00', '04:00', '08:00', '12:00', '16:00', '20:00'])
plt.xticks(rotation=90)
plt.xlabel('Absolute Time')
plt.ylabel('Temperature in °C')
plt.title("Heat Pump Thermostat Simulation (Variable Speed, Same Average)")
plt.legend(['Simulated Temperature', 'Input Target Tempearture'])
plt.figure(1).set_figwidth(15)
plt.subplots_adjust(top=0.88,
bottom=0.3,
left=0.055,
right=0.97,
hspace=0.2,
wspace=0.2)
plt.savefig("Heat_Pump_Thermostat_Simulation_VAR_SAME.pdf")
plt.show()

plt.plot(heating_power*power)
xlim = np.arange(0, n/dt, 60*60*4/dt)
plt.xticks(xlim, ['Day 1: 00:00', '04:00', '08:00', '12:00', '16:00', '20:00',
                   'Day 2: 00:00', '04:00', '08:00', '12:00', '16:00', '20:00',
                   'Day 3: 00:00', '04:00', '08:00', '12:00', '16:00', '20:00',
                   'Day 4: 00:00', '04:00', '08:00', '12:00', '16:00', '20:00',
                   'Day 5: 00:00', '04:00', '08:00', '12:00', '16:00', '20:00',
                   'Day 6: 00:00', '04:00', '08:00', '12:00', '16:00', '20:00',
                   'Day 7: 00:00', '04:00', '08:00', '12:00', '16:00', '20:00'])
plt.xticks(rotation=90)
plt.xlabel('Absolute Time   Total Power = ' + str(round(sum(heating_power)*power/60/1000)) + " KWh")
plt.ylabel('Power in W')
plt.title("Heat Pump Thermostat Simulation (Variable Speed, Same Average) - Heat Pump Power")
plt.figure(1).set_figwidth(15)
plt.subplots_adjust(top=0.88,
bottom=0.3,
left=0.055,
right=0.97,
hspace=0.2,
wspace=0.2)
plt.savefig("Heat_Pump_Thermostat_Simulation_Power_VAR_SAME.pdf")
plt.show()


# print(sum(heating)*power/60/1000)