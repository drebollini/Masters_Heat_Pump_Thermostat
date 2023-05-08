import numpy as np
import time
import pandas as pd
import matplotlib.pyplot as plt
plt.style.use('seaborn-poster')

data = pd.read_csv(r'data_exerpt_1.csv')
nest_data = pd.DataFrame(data, columns=['time', 'temp'])
nest_data_array = nest_data.to_numpy().transpose()

#constants
T_out = 5 #degrees C outside on the night of 1st-2nd December 2022 London City Airport
T_start = 22.18 #starting temperature indoors - from import data
alpha = 1000**4 #learning rate
alpha2 = 10
iters = 1000

#boundaries
n = 10*60*60 #10 hours by 15-min intervals
h = (60*60*10)/n #time between intervals

#heat ODE
def heat_ODE(T, k1, k2, T_out, q_in):
    return (1/k1)*(k2*(T-T_out)+q_in)
    
#differences method heat equ
def heat_equ(T, dt, k1, k2, T_out, q_in):
    return (dt*(k2*(T_out-T)+q_in)+(k1*T))/k1

#MSE
def mse(actual, predicted):
    actual = np.array(actual)
    predicted = np.array(predicted)
    differences = np.subtract(actual, predicted)
    squared_differences = np.square(differences)
    return squared_differences.mean()

def differences(actual, predicted):
    actual = np.array(actual)
    predicted = np.array(predicted)
    differences = np.subtract(actual, predicted)
    return differences

def parse_array(array, data_array_x_vals):
    return array[np.int_(data_array_x_vals)]

#Initiallise Values
A = np.zeros(n+1)
A[0] = T_start
error = 1
k1 = 1000*1000 #weight of air x Cp of air x fudge factor 
k2 = 584*2 #SA of house (11x8x9) x heat transfer coef. of 250mm brick
cost_history = []

Q_1 = np.zeros(n+1)

# A by same x values as data
A_parsed = parse_array(A, nest_data_array[0])

#Active Code
for i in range(iters):
    for k in range(0, n):
        A[k+1] = heat_equ(A[k],h,k1,k2,T_out,Q_1[k])

    #Grad descent
    error = mse(parse_array(A, nest_data_array[0]), nest_data_array[1])
    cost_history.append(error)
    print(error)
    k1 -= alpha*(1/len(A_parsed))*np.sum(differences(nest_data_array[0], A_parsed)*(1/(k1**2))*(k2*(T_out - parse_array(A, nest_data_array[0])) + parse_array(Q_1, nest_data_array[0])))
    k2 -= alpha2*(1/len(A_parsed))*np.sum(differences(nest_data_array[0], A_parsed)*((1/k1)*( - parse_array(A, nest_data_array[0]) + parse_array(Q_1, nest_data_array[0]))))
    # print(k1)
    # print(k2)

# A[1:] = heat_equ(A[:-1],h,k1,k2,T_out,Q_1[:-1])
for k in range(0, n):
    A[k+1] = heat_equ(A[k],h,k1,k2,T_out,Q_1[k])

plt.figure(figsize=(10,8))
plt.plot(A)
plt.plot(nest_data_array[0], nest_data_array[1])
# plt.ylim(15, 25)
plt.xlabel('time (sec)')
plt.ylabel('temp (deg)')
plt.show()

plt.figure(figsize=(10,8))
plt.plot(np.array(cost_history[5:]))
plt.show()

import json

themal_coefs = {"k1":k1, "k2":k2}
coef_str = json.dumps(themal_coefs)
coef_file = open("themal_coefs.json", "w")
coef_file.write(coef_str)
coef_file.close()
