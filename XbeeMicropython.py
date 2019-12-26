import xbee
from machine import ADC,Pin
import time
from math import fabs

temperaturePin = ADC('D0')
pressurePin = ADC('D1')
pumpPinOn = Pin("D2",Pin.OUT,value=0)
pumpPinOff = Pin("D3",Pin.OUT,value=0)
solenoidPin = Pin("D4",Pin.OUT,value=0)

witEndDevice   = b'\x00\x13\xa2\x00\x41\x98\x49\xde'
witCoordinator = b'\x00\x13\xa2\x00\x41\x97\xff\x02' #or just 0 would work too
response = ""

class pump:
	def __init__(self):
		pumpPinOn.value(0)
		pumpPinOff.value(1)
		time.sleep_ms(200)
		pumpPinOff.value(0)
		
	def On(self):
		pumpPinOff.value(0)
		pumpPinOn.value(1)
		time.sleep_ms(200)
		pumpPinOn.value(0)
		
	def Off(self):
		pumpPinOn.value(0)
		pumpPinOff.value(1)
		time.sleep_ms(200)
		pumpPinOff.value(0)
	
class solenoid:
	def __init__(self):
		pass
	
	def pressurize(self):
		solenoidPin.value(1)
		
	def depressurize(self):
		solenoidPin.value(0)
		
class pressureTransducer:
	def __init__(self):
		pass
		
	def read(self):
		return pressurePin.read()
		
class thermistor:
	def __init__(self):
		self.resistor = 15000 #ohm series resistor
		
	def read(self):
		return temperaturePin.read()

#discard all the packets waiting to be read
def discard():
	while xbee.receive():
		pass

#define all the objects
Pump = pump()
P = pressureTransducer()
T = thermistor()
sol = solenoid()

def runCycle(cycleTime, fluctuations):#this function needs to be fixed
	numberOfPoint = 48 #we should determine a safe value for the number of point we can send in one package
	dt = cycleTime//numOfPoint
	response.append(str(T.read())+",")
	sol.pressurize()
	start = time.ticks_ms()
	last5 = [0,0,0,0,0]
	i = 0
	currentP = P.read()
	while (time.ticks_diff(time.ticks_ms(),start)<cycleTime and fabs(currentP - last5.mean())>fluctuations):
		response.append(str(currentP)+",")
		last5[i]=currentP
		time.sleep_ms(dt)
		i += 1
		if i == 5:
			i = 0
		currentP = P.read()
	sol.depressurize()
	while (time.ticks_diff(time.ticks_ms(),start)<cycleTime):
		response.append(str(P.read())+",")
		time.sleep_ms(dt)
	response.append(str(T.read()))
	
def sendResponse():
	try:
		xbee.transmit(0, response) # send to the coordinator
		print("Data sent successfully")
	except Exception as e:
		print("Transmit failure: %s" % str(e))
			
While True:
	try:
		p = xbee.receive()
		if p:
			print(p['payload']
			response = ""
			if p['payload'] == "I":
				Pump.On()
				response = "Pump turned on"
			elif p['payload'] == "O":
				Pump.Off()
				response = "Pump turned off"
			elif "C" in p['payload']: #TODO: needs to be fixed
				cycleTime = int(p['payload']) #TODO: this needs to be fixed
			      	fluctuations = int(p['payload']) #TODO: this needs to be fixed
				runCycle(cycleTime, fluctuations)
			sendResponse() #sent the response back
			discard()
	except Exeption as e:
		print(str(e))
			     
