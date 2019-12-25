import xbee
from machine import ADC,Pin
import time

temperaturePin = ADC('D0')
pressurePin = ADC('D1')
pumpPinOn = Pin("D2",Pin.OUT,value=0)
pumpPinOff = Pin("D3",Pin.OUT,value=0)
solenoidPin = Pin("D4",Pin.OUT,value=0)

witEndDevice   = b'\x00\x13\xa2\x00\x41\x98\x49\xde'
witCoordinator = b'\x00\x13\xa2\x00\x41\x97\xff\x02' #or just 0 would work too

class pump:
	def __init__(self):
		pumpPinOff.value(1)
		time.sleep_ms(200)
		pumpPinOn.value(0)

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
while xbee.receive():
	discard = xbee.receive()

#define all the objects
Pump = pump()
P = pressureTransducer()
T = thermistor()
sol = solenoid()

def read():
	while True:
		p = xbee.receive()
		if p:
			print(p['payload'])
			start = time.ticks_ms()
			payloadT = str(T.read())
			payloadP = str(P.read())
			payload = p['payload'].decode('UTF-8')
			#print(payload1)
			if payload == 'T':
				sol.pressurize()
				xbee.transmit(0, payloadT  + '\r\n') #transmit temperature to the coordinator
				time.sleep_ms(100)
				sol.depressurize()
			if payload == 'P':
				sol.pressurize()
				xbee.transmit(0, payloadP + '\r\n')
				time.sleep_ms(100)
				sol.depressurize()
			print('time difference = ' + str(time.ticks_diff(time.ticks_ms(), start)) + ' milliseconds.')

While True:
	p = xbee.receive()
	if p:
		response = ""
		if p['payload'] == "I":
			Pump.On()
			response = "Pump turned on"
		elif p['payload'] == "O":
			Pump.Off()
			response = "Pump turned off"
		elif "C" in p['payload']:
			#figure out the set pressure and other info in the message
			runCycle()
		sendResponse() #sent the response back
