import numpy as np
import time
import pandas as pd
import matplotlib.pyplot as plt
plt.style.use('seaborn-poster')

##Functions
#heat ODE
def heat_ODE(T, k1, k2, T_out, q_in):
    return (1/k1)*(k2*(T-T_out)+q_in)
    
#differences method heat equ
def heat_equ(T, Q, dt, k1, k2, q_in, T_out):
    return (dt*(k2*(T_out-T)+q_in*Q)+(k1*T))/k1

#MSE
def mse(actual, predicted):
    differences = np.subtract(actual, predicted)
    squared_differences = np.square(differences)
    return squared_differences.mean()

def differences(actual, predicted):
    differences = np.subtract(actual, predicted)
    return differences

def rescale_array(array, dt, data_array_x_vals):
    return array[np.int_(data_array_x_vals/dt)]

##Setup
#Import data
data = pd.read_csv(r'data_exerpt_5.csv', header=None)
nest_data_array = data.to_numpy()

print(nest_data_array)

#Constants
T_out = 9.5 #degrees C outside on the night of 1st-2nd December 2022 London City Airport

#Learning Rates & Iterations
alpha1 = 1000**5 #learning rate
alpha2 = 10
alpha3 = 1000**2*100
iters = 50000

#Boundaries
boundary = nest_data_array[-1, 0]

#Resolution
res = 60 #resolution in seconds pls be divisible into 900)

#Initialise Values
t_data = nest_data_array[:, 0]
A_data = nest_data_array[:, 1]
Q_data = nest_data_array[:, 2]

h = int(boundary) #total seconds
n = int(h/res) #no.of intervals
dt = int(res) #time step

t = np.append(np.arange(0, h, dt), h)
A = np.zeros(n+1) #temp array
A[0] =  A_data[0] #set temp array equal to start temp
Q = np.zeros(n+1)

print(boundary)
print(len(t_data), len(A_data), len(Q_data))
print(len(t), len(A), len(Q))


#Fill Q Array
for i in range(0, len(t_data)-1):
    Q[int(t_data[i]/dt):int(t_data[i+1]/dt)] = int(Q_data[i])

# A_parsed = rescale_array(A, dt, t_data)
# Q_parsed = rescale_array(Q, dt, t_data)

error = 0 #initalise error

k1 = 1000*1000 #weight of air x Cp of air x fudge factor 
k2 = 584*2 #SA of house (11x8x9) x heat transfer coef. of 250mm brick
q_in = 3000 #power of heater

cost_history = []

#Active Code
for i in range(iters):
    for k in range(0, n):
        A[k+1] = heat_equ(A[k],Q[k],dt,k1,k2,q_in,T_out)

    #Grad descent
    error = mse(rescale_array(A, dt, t_data), A_data)
    cost_history.append(error)
    print(error)
    k1 -= alpha1*(1/len(rescale_array(A, dt, t_data)))*np.sum(differences(A_data, rescale_array(A, dt, t_data))*(1/(k1**2))*(k2*(T_out - rescale_array(A, dt, t_data)) + rescale_array(Q, dt, t_data)))
    k2 -= alpha2*(1/len(rescale_array(A, dt, t_data)))*np.sum(differences(A_data, rescale_array(A, dt, t_data))*((1/k1)*( - rescale_array(A, dt, t_data)) + rescale_array(Q, dt, t_data)))
    q_in -= alpha3*(1/len(rescale_array(A, dt, t_data)))*np.sum(differences(A_data, rescale_array(A, dt, t_data))*(1/k1))

# A[1:] = heat_equ(A[:-1],h,k1,k2,T_out,Q_1[:-1])
# for k in range(0, n):
#     A[k+1] = heat_equ(A[k],Q[k],dt,k1,k2,q_in,T_out)



plt.figure(figsize=(10,8))
plt.plot(t, A)
plt.plot(t_data, A_data)
# plt.ylim(15, 25)
plt.xlabel('time (sec)')
plt.ylabel('temp (deg)')
plt.show()

plt.figure(figsize=(10,8))
plt.plot(np.array(cost_history[50:]))
plt.show()

import json

themal_coefs = {"k1":k1, "k2":k2, "q_in":q_in}
coef_str = json.dumps(themal_coefs)
coef_file = open("themal_coefs.json", "w")
coef_file.write(coef_str)
coef_file.close()
