import xbee
from machine import ADC,Pin
import time

temperaturePin = ADC('D0')
pressurePin = ADC('D1')
pumpPinOn = Pin('D2',Pin.OUT,value=0)
pumpPinOff = Pin('D3',Pin.OUT,value=0)
solenoidPin = Pin('D4',Pin.OUT,value=0)

witEndDevice   = b'\x00\x13\xa2\x00\x41\x98\x49\xde'
witCoordinator = b'\x00\x13\xa2\x00\x41\x97\xff\x02' #or just 0 would work too
response = ''

def fabs(number):
	if number < 0 :
		number *= -1
	return number

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
		
def mean(l):
	return sum(l)/len(l)
	

#define all the objects
Pump = pump()
P = pressureTransducer()
T = thermistor()
sol = solenoid()

def runCycle(cycleTime, fluctuations, numberOfPoints = 20):#this function needs to be fixed
	global response
	dt = cycleTime//numberOfPoints
	response = response + str(T.read()) + ','
	currentP = P.read()
	sol.pressurize()
	start = time.ticks_ms()
	last5 = [0,0,0]
	i = 0
	while (time.ticks_diff(time.ticks_ms(),start)<=cycleTime and (fabs(currentP - mean(last5)>fluctuations) or currentP < 500)):
		response = response + str(currentP) + ','
		last5[i]=currentP
		time.sleep_ms(dt)
		i += 1
		if i == 3:
			i = 0
		currentP = P.read() #read 5 points and average them out
	sol.depressurize()
	while (time.ticks_diff(time.ticks_ms(),start)<=cycleTime):
		response = response + str(P.read()) + ','
		time.sleep_ms(dt)
	response = response + str(T.read())
	
def sendResponse():
	try:
		xbee.transmit(0, response) # send to the coordinator
		#print("Data sent successfully")
	except Exception as e:
		print("Transmit failure: %s" % str(e))

while True:
	p = xbee.receive()
	if p:
		#print(p['payload'])
		response = ""
		if p['payload'] == b'I':
			Pump.On()
			response = 'Pump turned on'
		elif p['payload'] == b'O':
			Pump.Off()
			response = 'Pump turned off'
		elif 'C' in p['payload']: #TODO: needs to be fixed
			payloadInfo = p['payload'].split()
			#print(payloadInfo)
			cycleTime = int(payloadInfo[1])
			fluctuations = int(payloadInfo[2])
			numberOfPoints = int(payloadInfo[3])
			runCycle(cycleTime, fluctuations, numberOfPoints)
		sendResponse() #sent the response back
		discard()
