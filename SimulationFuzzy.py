import numpy as np
import matplotlib.pyplot as plt
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from scipy import signal

# Define fuzzy input parameters (from optimization or manual tuning)
parameters = [-8 ,-8, -5.333,-8, -5.333, -2.667,-5.333 ,-2.667 ,0,-2.667 ,0 ,2.667,0 ,2.667 ,5.333,2.667 ,5.333 ,8,5.333 ,8 ,8,-4 ,-4 ,-2.667,-4, -2.667, -1.333,-2.667, -1.333 ,0,-1.333 ,0 ,1.333,0 ,1.333 ,2.667,1.333 ,2.667 ,4,2.667 ,4 ,4,5]

# Extract and sort subsets for universe ranges
a = sorted(parameters[0:3])
b = sorted(parameters[18:21])
c = sorted(parameters[21:24])
d = sorted(parameters[39:42])

# Define fuzzy input and output variables
error = ctrl.Antecedent(np.linspace(a[0], b[2], 1000), 'error')
delta_error = ctrl.Antecedent(np.linspace(c[0], d[2], 1000), 'delta_error')
control_output = ctrl.Consequent(np.linspace(0, 255, 1000), 'control_output')

# Optional: printing parameter subsets for inspection
print(sorted(parameters[0:3]))
print(sorted(parameters[18:21]))
print(sorted(parameters[21:24]))
print(sorted(parameters[39:42]))
print(sorted(parameters[42:45]))

# Define fuzzy membership functions for error
error['NB'] = fuzz.trimf(error.universe, sorted(parameters[0:3]))
error['NM'] = fuzz.trimf(error.universe, sorted(parameters[3:6]))
error['NS'] = fuzz.trimf(error.universe, sorted(parameters[6:9]))
error['ZE'] = fuzz.trimf(error.universe, sorted(parameters[9:12]))
error['PS'] = fuzz.trimf(error.universe, sorted(parameters[12:15]))
error['PM'] = fuzz.trimf(error.universe, sorted(parameters[15:18]))
error['PB'] = fuzz.trimf(error.universe, sorted(parameters[18:21]))

# Define fuzzy membership functions for delta_error
delta_error['NB'] = fuzz.trimf(delta_error.universe, sorted(parameters[21:24]))
delta_error['NM'] = fuzz.trimf(delta_error.universe, sorted(parameters[24:27]))
delta_error['NS'] = fuzz.trimf(delta_error.universe, sorted(parameters[27:30]))
delta_error['ZE'] = fuzz.trimf(delta_error.universe, sorted(parameters[30:33]))
delta_error['PS'] = fuzz.trimf(delta_error.universe, sorted(parameters[33:36]))
delta_error['PM'] = fuzz.trimf(delta_error.universe, sorted(parameters[36:39]))
delta_error['PB'] = fuzz.trimf(delta_error.universe, sorted(parameters[39:42]))

# Define fuzzy membership functions for control output
control_output['ZE'] = fuzz.trimf(control_output.universe, [0, 32.5, 65])
control_output['PS'] = fuzz.trimf(control_output.universe, [65, 112.5, 160])
control_output['PM'] = fuzz.trimf(control_output.universe, [112.5, 160, 207.5])
control_output['PB'] = fuzz.trimf(control_output.universe, [160, 207.5, 255])

# Define fuzzy rules for the control logic
rules = [
    ctrl.Rule(error['NB'] & delta_error['NB'], control_output['PB']),
    ctrl.Rule(error['NB'] & delta_error['NM'], control_output['PB']),
    ctrl.Rule(error['NB'] & delta_error['NS'], control_output['PB']),
    ctrl.Rule(error['NB'] & delta_error['ZE'], control_output['PM']),
    ctrl.Rule(error['NB'] & delta_error['PS'], control_output['PM']),
    ctrl.Rule(error['NB'] & delta_error['PM'], control_output['PS']),
    ctrl.Rule(error['NB'] & delta_error['PB'], control_output['ZE']),
     
    ctrl.Rule(error['NM'] & delta_error['NB'], control_output['PB']),
    ctrl.Rule(error['NM'] & delta_error['NM'], control_output['PB']),
    ctrl.Rule(error['NM'] & delta_error['NS'], control_output['PM']),
    ctrl.Rule(error['NM'] & delta_error['ZE'], control_output['PM']),
    ctrl.Rule(error['NM'] & delta_error['PS'], control_output['PS']),
    ctrl.Rule(error['NM'] & delta_error['PM'], control_output['ZE']),
    ctrl.Rule(error['NM'] & delta_error['PB'], control_output['ZE']),
    
    ctrl.Rule(error['NS'] & delta_error['NB'], control_output['PM']),
    ctrl.Rule(error['NS'] & delta_error['NM'], control_output['PM']),
    ctrl.Rule(error['NS'] & delta_error['NS'], control_output['PM']),
    ctrl.Rule(error['NS'] & delta_error['ZE'], control_output['PS']),
    ctrl.Rule(error['NS'] & delta_error['PS'], control_output['ZE']),
    ctrl.Rule(error['NS'] & delta_error['PM'], control_output['ZE']),
    ctrl.Rule(error['NS'] & delta_error['PB'], control_output['ZE']),
    
    ctrl.Rule(error['ZE'] & delta_error['NB'], control_output['PM']),
    ctrl.Rule(error['ZE'] & delta_error['NM'], control_output['PM']),
    ctrl.Rule(error['ZE'] & delta_error['NS'], control_output['PS']),
    ctrl.Rule(error['ZE'] & delta_error['ZE'], control_output['ZE']),
    ctrl.Rule(error['ZE'] & delta_error['PS'], control_output['ZE']),
    ctrl.Rule(error['ZE'] & delta_error['PM'], control_output['ZE']),
    ctrl.Rule(error['ZE'] & delta_error['PB'], control_output['ZE']),
    
    ctrl.Rule(error['PS'] & delta_error['NB'], control_output['PM']),
    ctrl.Rule(error['PS'] & delta_error['NM'], control_output['PS']),
    ctrl.Rule(error['PS'] & delta_error['NS'], control_output['ZE']),
    ctrl.Rule(error['PS'] & delta_error['ZE'], control_output['ZE']),
    ctrl.Rule(error['PS'] & delta_error['PS'], control_output['ZE']),
    ctrl.Rule(error['PS'] & delta_error['PM'], control_output['ZE']),
    ctrl.Rule(error['PS'] & delta_error['PB'], control_output['ZE']),
    
    ctrl.Rule(error['PM'] & delta_error['NB'], control_output['PS']),
    ctrl.Rule(error['PM'] & delta_error['NM'], control_output['ZE']),
    ctrl.Rule(error['PM'] & delta_error['NS'], control_output['ZE']),
    ctrl.Rule(error['PM'] & delta_error['ZE'], control_output['ZE']),
    ctrl.Rule(error['PM'] & delta_error['PS'], control_output['ZE']),
    ctrl.Rule(error['PM'] & delta_error['PM'], control_output['ZE']),
    ctrl.Rule(error['PM'] & delta_error['PB'], control_output['ZE']),
    
    ctrl.Rule(error['PB'] & delta_error['NB'], control_output['ZE']),
    ctrl.Rule(error['PB'] & delta_error['NM'], control_output['ZE']),
    ctrl.Rule(error['PB'] & delta_error['NS'], control_output['ZE']),
    ctrl.Rule(error['PB'] & delta_error['ZE'], control_output['ZE']),
    ctrl.Rule(error['PB'] & delta_error['PS'], control_output['ZE']),
    ctrl.Rule(error['PB'] & delta_error['PM'], control_output['ZE']),
    ctrl.Rule(error['PB'] & delta_error['PB'], control_output['ZE'])
]

# Create and simulate the fuzzy controller
fuzzy_control_system = ctrl.ControlSystem(rules)
fuzzy_controller = ctrl.ControlSystemSimulation(fuzzy_control_system)

# Define simulation parameters
time_duration = 100  # Total simulation time [seconds]
time_steps = np.linspace(0, time_duration, num=1000)
target_value = 25.01  # Desired moisture level [%]

# Create the plant (system) transfer function
num = [288.1953]
den = [1905.6066, 1]
system = signal.TransferFunction(num, den)

# Helper function to saturate values within limits
def saturate(value, lower_limit, upper_limit):
    return np.clip(value, lower_limit, upper_limit)

# Initialize arrays to store simulation data
system_output = np.zeros_like(time_steps)
control_signal = np.zeros_like(time_steps)
error_signal = np.zeros_like(time_steps)

# Run simulation loop
for i, t in enumerate(time_steps):
    if i == 0:
        system_output[i] = 0
    else:
        # Compute error and change in error
        error = system_output[i-1] - target_value
        error_signal[i] = saturate(error, -8, 8)
        delta_e = error_signal[i] - error_signal[i-1]
        delta_e_saturated = saturate(delta_e, -4, 4)
        
        # Fuzzify inputs and compute output
        fuzzy_controller.input['error'] = error_signal[i]
        fuzzy_controller.input['delta_error'] = delta_e_saturated
        fuzzy_controller.compute()
        
        # Apply control decision
        if fuzzy_controller.output['control_output'] < 65:
            control_signal[i] = 0
        else:
            control_signal[i] = fuzzy_controller.output['control_output']

        # Simulate system response
        _, y_out, _ = signal.lsim(system, U=control_signal[:i+1], T=time_steps[:i+1])
        system_output[i] = y_out[-1]

# Define function to calculate settling time
def calculate_settling_time(t, y, percentage=5, min_duration=1.0):
    final_value = y[-1]
    tolerance = final_value * (percentage / 100)
    settling_time = t[-1]
    
    for i in range(len(y)):
        if np.abs(y[i] - final_value) <= tolerance:
            sustained = True
            for j in range(i, len(y)):
                if np.abs(y[j] - final_value) > tolerance:
                    sustained = False
                    break
                if t[j] - t[i] >= min_duration:
                    settling_time = t[i]
                    return settling_time
    return settling_time

# Calculate performance metrics
errorov = np.array(system_output - target_value)
overshoot = max(system_output) - target_value
settling_time = calculate_settling_time(time_steps, system_output, percentage=2, min_duration=2)

settling_index = next(i for i, t in enumerate(time_steps) if t >= settling_time)
error_stable = abs(target_value - np.mean(system_output[settling_index:]))
rmse = np.sqrt(np.mean(errorov ** 2))
mae = np.mean(np.abs(errorov))
iae = np.sum(np.abs(errorov)) * (time_steps[1] - time_steps[0])
itae = np.sum(time_steps * np.abs(errorov)) * (time_steps[1] - time_steps[0])

# Print system performance
print("\nSystem Performance Metrics:")
print(f"  Steady-State Error      : {error_stable:.4f}")
print(f"  Overshoot               : {overshoot:.4f}")
print(f"  Settling Time (s)        : {settling_time:.2f}")
print(f"  RMSE                    : {rmse:.4f}")
print(f"  MAE                     : {mae:.4f}")
print(f"  IAE                     : {iae:.4f}")
print(f"  ITAE                    : {itae:.4f}")
print(f"  Total Composite Metric  : {rmse + mae  + iae + itae:.4f}")

# Plot system response
plt.plot(time_steps, system_output, label="System Output")
plt.axhline(y=target_value, color='r', linestyle='--', label=f"Target ({target_value})")
plt.xlabel('Time [s]')
plt.ylabel('Soil Moisture (%)')
plt.title(f"System Response with Fuzzy Logic Control (Target = {target_value})")
plt.legend()
plt.grid()
plt.show()
