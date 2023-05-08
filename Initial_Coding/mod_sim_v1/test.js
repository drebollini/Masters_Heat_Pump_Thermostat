const fs = require('fs');
const coef_file = fs.readFileSync("themal_coefs.json");
const coef_JSON = coef_file.toString();
const coef = JSON.parse(coef_JSON);

console.log("eat my ass")

//constants
const power = coef['q_in']; //heater power/W
const T_out = 9.5; //degrees C outside on the night of 1st-2nd December 2022 London City Airport
const T_start = 22.18; //starting temperature indoors - from import data
const k1 = coef['k1'];
const k2 = coef['k2'];

//boundaries
const n = 24*60*60; //24 hours in sec
const dt = 60; //interval time in seconds
const h = Math.floor(n/dt); //no. of intervals

//Thermostat
const thermostat_target = 20; //thermostat target at end of boundary

//heat ODE
function heat_ODE(T, k1, k2, T_out, q_in){
    return (1/k1)*(k2*(T-T_out)+q_in);
}

//differences method heat equ
function heat_equ(T, dt, k1, k2, T_out, q_in){
    return (dt*(k2*(T_out-T)+q_in)+(k1*T))/k1;
}

//backwards differences method heat equ
function heat_equ_back(T, dt, k1, k2, T_out, q_in){
    return -(dt*(k2*(T_out-T)+q_in)-(k1*T))/k1;
}

//Bang-bang algorithm
let temp_heating = new Array(h+1).fill(0);
temp_heating[h] = thermostat_target;
let temp_cooling = new Array(h+1).fill(0);
temp_cooling[0] = T_start;
let heating = new Array(h+1).fill(1);

temp_heating = temp_heating.reverse();
for (let k = 0; k < h; k++){
    temp_heating[k+1] = heat_equ_back(temp_heating[k], dt, k1, k2, T_out, power*heating[k]);
}
temp_heating = temp_heating.reverse();

for (let k = 0; k < h; k++){
    temp_cooling[k+1] = heat_equ(temp_cooling[k], dt, k1, k2, T_out, 0);
}

for (let k = 0; k < h; k++){
    if (temp_heating[k] < temp_cooling[k]){
        heating[k] = 0;
    }
    if (temp_heating[k] > temp_cooling[k]){
        heating[k] = 1;
    }
}

let temp = new Array(h+1).fill(0);
temp[0] = T_start;
for (let k = 0; k < h; k++){
    temp[k+1] = heat_equ(temp[k], dt, k1, k2, T_out, power*heating[k]);
}

console.log(temp);

const plt = require('matplotlib-js');
plt.style.use('seaborn-poster');

plt.plot(temp);
plt.ylim(15, 25);
plt.xlabel('time (sec)');
plt.ylabel('temp (deg)');
plt.show();

plt.plot(heating);
plt.show();