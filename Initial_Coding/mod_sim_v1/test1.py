import numpy as np
import matplotlib.pyplot as plt
plt.style.use('seaborn-poster')

#constants
k1 = 1000*1000*15 #weight of air x Cp of air x fudge factor 
k2 = 518*2*0.5 # SA of house (11x8x9) x heat transfer coef. of 250mm brick
q_in = 27000 #heater power/W
T_out = 5 #degrees C outside on the night of 1st-2nd December 2022 London City Airport
T_start = 21 #starting temperature indoors

#boundaries
n = 24*60 #day by 15-min intervals
h = (60*60*24)/n #time between intervals

#heat ODE
def heat_equ(T, dt, k1, k2, T_out, q_in):
    T_1 = (dt*(k2*(T_out-T)+q_in)+(k1*T))/k1
    return T_1

#temp array
A = np.zeros(n+1)
A[0] = T_start
print(A)

#power array
Q = np.zeros(n+1) 
Q[0:15] = q_in
Q[75:90] = q_in
Q[150:165] = q_in
print(Q)

for i in range(0, n):
    A[i+1] = heat_equ(A[i], h, k1, k2, T_out, Q[i])

print(A)

plt.figure(figsize=(10,8))
plt.plot(A)
plt.ylim(0, 50)
plt.xlabel('time (min)')
plt.ylabel('temp (deg)')
plt.show()
