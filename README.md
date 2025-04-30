# Fuzzy-GA-Control-On-Soil-Humidity
Using Fuzzy-GA to control actuators that is a water pump that provide water for soil humidity.

#### SimulationFuzzy.py
This file is used as a simulation of fuzzy controlled system using membership function that tuned manually.

## SimulationFGA.py
This file is used as a simulation that the MF(Membership Function) is getting from GA tuned MF.

## MembershipTunerGA.py 
This file is used to generate MF that tuned by GA.

## espflask.py
This file is used as a server for transferring data from esp32 to database and host(computer) and the other way around using HTTP protocol.

## esp32.ino
This file is used as C code for esp32 that read the sensor data and sending the data to server and give output of the fuzzy.

## FuzzyO.py and FuzzyGA.py
This file is used as a function, the function count output based on the input of the sensor. the diffrence between the two is the membership function only, one is tuned manuallt and one is using GA.
