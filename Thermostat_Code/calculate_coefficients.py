import numpy as np
import time
import pandas as pd
import matplotlib.pyplot as plt
import json

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
def import_data(data_location):
    data = pd.read_csv(data_location, header=None)
    data_array = data.to_numpy()
    return (data_array)

def calculate_coefficients(data_location):
    nest_data_array = import_data(data_location)

    #Learning Rates & Iterations
    alpha1 = 1000**5 #learning rate
    alpha2 = 10
    alpha3 = 1000**2*100
    iters = 100000

    #Set Boundaries
    boundary = nest_data_array[-1, 0]

    #Set Resolution
    res = 60 #resolution in seconds pls be divisible into 900)

    #Initialise Values
    t_data = nest_data_array[:, 0]
    A_data = nest_data_array[:, 1]
    Q_data = nest_data_array[:, 2]
    T_out_data = nest_data_array[:, 3]

    h = int(boundary) #total seconds
    n = int(h/res) #no.of intervals
    dt = int(res) #time step

    t = np.append(np.arange(0, h, dt), h)
    A = np.zeros(n+1) #temp array
    A[0] =  A_data[0] #set temp array equal to start temp
    Q = np.zeros(n+1)
    T_out = np.zeros(n+1)

    error = 0 #initalise error

    k1 = 1000*1000 #weight of air x Cp of air x fudge factor 
    k2 = 584*2 #SA of house (11x8x9) x heat transfer coef. of 250mm brick
    q_in = 3000 #power of heater

    cost_history = []

    #Fill Q Array
    for i in range(0, len(t_data)-1):
        Q[int(t_data[i]/dt):int(t_data[i+1]/dt)] = int(Q_data[i])

    #Fill T_out Array
    for i in range(0, len(t_data)-1):
        T_out[int(t_data[i]/dt):int(t_data[i+1]/dt)] = T_out_data[i]

    #Calculate Coefficients
    for i in range(iters):
        for k in range(0, n):
            A[k+1] = heat_equ(A[k],Q[k],dt,k1,k2,q_in,T_out[k])

        #Grad descent
        error = mse(rescale_array(A, dt, t_data), A_data)
        cost_history.append(error)
        print(error)
        k1 -= alpha1*(1/len(rescale_array(A, dt, t_data)))*np.sum(differences(A_data, rescale_array(A, dt, t_data))*(1/(k1**2))*(k2*(T_out_data - rescale_array(A, dt, t_data)) + rescale_array(Q, dt, t_data)))
        k2 -= alpha2*(1/len(rescale_array(A, dt, t_data)))*np.sum(differences(A_data, rescale_array(A, dt, t_data))*((1/k1)*( - rescale_array(A, dt, t_data)) + rescale_array(Q, dt, t_data)))
        q_in -= alpha3*(1/len(rescale_array(A, dt, t_data)))*np.sum(differences(A_data, rescale_array(A, dt, t_data))*(1/k1))

    themal_coefs = {"k1":k1, "k2":k2, "q_in":q_in}
    coef_str = json.dumps(themal_coefs)
    coef_file = open("thermal_coefs_1.json", "w")
    coef_file.write(coef_str)
    coef_file.close()

    return()

calculate_coefficients(r'Thermostat_Code\historical_data.csv')
