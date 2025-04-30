import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

def create_fuzzy_control_system():
    # Step 1: Define fuzzy input variables
    dsm = ctrl.Antecedent(np.linspace(-8, 8, 1000), 'dsm')  # Error (-6 to 6)
    ecr = ctrl.Antecedent(np.linspace(-4, 4, 1000), 'ecr')  # Error Change Rate (-3 to 3)

    # Define fuzzy output variable
    u = ctrl.Consequent(np.linspace(0, 255, 1000), 'u')  # Control signal (65 to 255)
    
    parameters= [-8.0, -8.0, -5.226974118833155, -8.0, -5.4084042953148215, -3.144040766836488, -5.513317972457319, -2.667, 0.0, -2.664593899972617, 0.0, 2.667, 0.0, 2.5998691342863562, 5.33279821731613, 2.8394357624839364, 5.333, 7.981377440315914, 5.309052658451995, 8.0, 8.0, -3.9489486998479304, -4.314176808411542, -2.2597656080230375, -5.506606874045708, -2.6419974143719243, -1.3330000000000002, -2.620289383913542, -1.5046472984684414, 0.0, -1.9595934737228347, -1.4447926110412523, 1.2664941486911725, 0.3486589961823055, 1.7688150283967414, 2.667, 1.2730086555619229, 2.667, 3.9944755478667755, 1.0213223595050653, 6.069881668169481, 5.716886275402469, 4.61763516892221,0, 32.5, 65,65, 112.5, 160,112.5, 160, 207.5,160, 207.5, 255]


    dsm['NB'] = fuzz.trimf(dsm.universe, sorted(parameters[0:3]))
    dsm['NM'] = fuzz.trimf(dsm.universe, sorted(parameters[3:6]))
    dsm['NS'] = fuzz.trimf(dsm.universe, sorted(parameters[6:9]))
    dsm['ZE'] = fuzz.trimf(dsm.universe, sorted(parameters[9:12]))
    dsm['PS'] = fuzz.trimf(dsm.universe, sorted(parameters[12:15]))
    dsm['PM'] = fuzz.trimf(dsm.universe, sorted(parameters[15:18]))
    dsm['PB'] = fuzz.trimf(dsm.universe, sorted(parameters[18:21]))

    ecr['NB'] = fuzz.trimf(ecr.universe, sorted(parameters[21:24]))
    ecr['NM'] = fuzz.trimf(ecr.universe, sorted(parameters[24:27]))
    ecr['NS'] = fuzz.trimf(ecr.universe, sorted(parameters[27:30]))
    ecr['ZE'] = fuzz.trimf(ecr.universe, sorted(parameters[30:33]))
    ecr['PS'] = fuzz.trimf(ecr.universe, sorted(parameters[33:36]))
    ecr['PM'] = fuzz.trimf(ecr.universe, sorted(parameters[36:39]))
    ecr['PB'] = fuzz.trimf(ecr.universe, sorted(parameters[39:42]))



    # Fuzzy membership functions for control output
    u['ZE'] = fuzz.trimf(u.universe, sorted(parameters[42:45]))
    u['PS'] = fuzz.trimf(u.universe, sorted(parameters[45:48]))
    u['PM'] = fuzz.trimf(u.universe, sorted(parameters[48:51]))
    u['PB'] = fuzz.trimf(u.universe, sorted(parameters[51:54]))


    # Step 3: Define fuzzy rules
    rules = [
        ctrl.Rule(dsm['NB'] & ecr['NB'], u['PB']),
        ctrl.Rule(dsm['NB'] & ecr['NM'], u['PB']),
        ctrl.Rule(dsm['NB'] & ecr['NS'], u['PB']),
        ctrl.Rule(dsm['NB'] & ecr['ZE'], u['PM']),
        ctrl.Rule(dsm['NB'] & ecr['PS'], u['PM']),
        ctrl.Rule(dsm['NB'] & ecr['PM'], u['PS']),
        ctrl.Rule(dsm['NB'] & ecr['PB'], u['ZE']),
        
        ctrl.Rule(dsm['NM'] & ecr['NB'], u['PB']),
        ctrl.Rule(dsm['NM'] & ecr['NM'], u['PB']),
        ctrl.Rule(dsm['NM'] & ecr['NS'], u['PM']),
        ctrl.Rule(dsm['NM'] & ecr['ZE'], u['PM']),
        ctrl.Rule(dsm['NM'] & ecr['PS'], u['PS']),
        ctrl.Rule(dsm['NM'] & ecr['PM'], u['ZE']),
        ctrl.Rule(dsm['NM'] & ecr['PB'], u['ZE']),
        
        ctrl.Rule(dsm['NS'] & ecr['NB'], u['PM']),
        ctrl.Rule(dsm['NS'] & ecr['NM'], u['PM']),
        ctrl.Rule(dsm['NS'] & ecr['NS'], u['PM']),
        ctrl.Rule(dsm['NS'] & ecr['ZE'], u['PS']),
        ctrl.Rule(dsm['NS'] & ecr['PS'], u['ZE']),
        ctrl.Rule(dsm['NS'] & ecr['PM'], u['ZE']),
        ctrl.Rule(dsm['NS'] & ecr['PB'], u['ZE']),
        
        ctrl.Rule(dsm['ZE'] & ecr['NB'], u['PM']),
        ctrl.Rule(dsm['ZE'] & ecr['NM'], u['PM']),
        ctrl.Rule(dsm['ZE'] & ecr['NS'], u['PS']),
        ctrl.Rule(dsm['ZE'] & ecr['ZE'], u['ZE']),
        ctrl.Rule(dsm['ZE'] & ecr['PS'], u['ZE']),
        ctrl.Rule(dsm['ZE'] & ecr['PM'], u['ZE']),
        ctrl.Rule(dsm['ZE'] & ecr['PB'], u['ZE']),
        
        ctrl.Rule(dsm['PS'] & ecr['NB'], u['PM']),
        ctrl.Rule(dsm['PS'] & ecr['NM'], u['PS']),
        ctrl.Rule(dsm['PS'] & ecr['NS'], u['ZE']),
        ctrl.Rule(dsm['PS'] & ecr['ZE'], u['ZE']),
        ctrl.Rule(dsm['PS'] & ecr['PS'], u['ZE']),
        ctrl.Rule(dsm['PS'] & ecr['PM'], u['ZE']),
        ctrl.Rule(dsm['PS'] & ecr['PB'], u['ZE']),
        
        ctrl.Rule(dsm['PM'] & ecr['NB'], u['PS']),
        ctrl.Rule(dsm['PM'] & ecr['NM'], u['ZE']),
        ctrl.Rule(dsm['PM'] & ecr['NS'], u['ZE']),
        ctrl.Rule(dsm['PM'] & ecr['ZE'], u['ZE']),
        ctrl.Rule(dsm['PM'] & ecr['PS'], u['ZE']),
        ctrl.Rule(dsm['PM'] & ecr['PM'], u['ZE']),
        ctrl.Rule(dsm['PM'] & ecr['PB'], u['ZE']),
        
        ctrl.Rule(dsm['PB'] & ecr['NB'], u['ZE']),
        ctrl.Rule(dsm['PB'] & ecr['NM'], u['ZE']),
        ctrl.Rule(dsm['PB'] & ecr['NS'], u['ZE']),
        ctrl.Rule(dsm['PB'] & ecr['ZE'], u['ZE']),
        ctrl.Rule(dsm['PB'] & ecr['PS'], u['ZE']),
        ctrl.Rule(dsm['PB'] & ecr['PM'], u['ZE']),
        ctrl.Rule(dsm['PB'] & ecr['PB'], u['ZE'])
    ]

    control_system = ctrl.ControlSystem(rules)
    return ctrl.ControlSystemSimulation(control_system)

def saturate(value, lower_limit, upper_limit):
    return np.clip(value, lower_limit, upper_limit)

def compute_control_signal(dsm_input, ecr_input):
    simulation = create_fuzzy_control_system()
    simulation.input['dsm'] = saturate(dsm_input, -8, 8)
    simulation.input['ecr'] = saturate(ecr_input, -4, 4)
    simulation.compute()
    if simulation.output['u']< 65:
        control_signal=0
    else:
        control_signal=simulation.output['u']
    return control_signal
