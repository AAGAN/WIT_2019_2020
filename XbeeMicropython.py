import xbee
import machine
import time

pressurePin = machine.ADC('D1')

temperaturePin = machine.ADC('D0')

pumpPinOn = machine.Pin.board.D2
pumpPinOff = machine.Pin.board.D3
pumpPinOn.mode(machine.Pin.OUT)
pumpPinOff.mode(machine.Pin.OUT)
pumpPinOff.value(0)
pumpPinOn.value(0)

solenoidPin = machine.Pin.board.D4
solenoidPin.mode(machine.Pin.OUT)
solenoidPin.value(0)

#Coordinator = b'\x00\x13\xa2\x00\x41\x93\xf6\x4b' 
#EndDevice1  = b'\x00\x13\xa2\x00\x41\x92\xcd\xf3'
#EndDevice2  = b'\x00\x13\xa2\x00\x41\x95\xce\x13'
#EndDevice3  = b'\x00\x13\xa2\x00\x41\x92\xdc\x03'

witEndDevice   = b'\x00\x13\xa2\x00\x41\x98\x49\xde'
witCoordinator = b'\x00\x13\xa2\x00\x41\x97\xff\x02' #or just 0 would work too

class pump:
	def __init__(self):
		pumpPinOff.value(1)
		time.sleep_ms(200)
		pumpPinOn.value(0)

	def turnOn(self):
		pumpPinOff.value(0)
		pumpPinOn.value(1)
		time.sleep_ms(200)
		pumpPinOn.value(0)
		
	def turnOff(self):
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
		
	def readRawADCPressure(self):
		return pressurePin.read()
		
	def readVoltageOnPressure(self):
		voltage = self.readRawADCPressure()*3.3/4095
		return voltage
		
	def readPsiPressure(self):
		minVoltage = 0.328 #corresponding to 0.5V (R1 = 10.5kohm and R2 = 20 kohm) and 0psi
		maxVoltage = 2.951 #corresponding to 4.5V (R1 = 10.5kohm and R2 = 20 kohm) and 1000psi
		maxPressure = 1000 #psi
		minPressure = 0    #psi
		pressure = (self.readVoltageOnPressure() - minVoltage) / (maxVoltage - minVoltage) * (maxPressure-minPressure)
		return pressure
		
	#averages 20 readings and returns the pressure in psi for the 1000psi guage transducer
	def psi(self):
		p = 0.0
		for _ in range(20):
			p += pressurePin.read()
			time.sleep_ms(2)
		p /= 20.0
		return p * 0.3072533 #(p*3.3/4095-0.328)/(2.951-0.328)*1000
		
		
class thermistor:
	def __init__(self):
		self.resistor = 15000 #ohm series resistor
		
	def readRawADCTemperature(self):
		return temperaturePin.read()
	
	def readResistanceOnTempertuare(self):
		reading = (4095 / readRawADCTemperature())-1.0
		reading = self.resistor / reading
		return reading
		
	def F(self):
		return temperaturePin.read()
		#tempF = 0
		#for _ in range(10):
		#	tempF += temperaturePin.read()
		#	time.sleep_ms(2)
		#tempF /= 10
		#tempF = 4095/ tempF -1
		#tempF = self.resistor / tempF
		#
		#tempF = tempF / 10000 #THERMISTORNOMINAL
		#tempF = log(tempF)
		#tempF /= 3950 #BCOEFFICIENT
		#tempF += 1.0 / (25.0 + 273.15)
		#tempF = 1.0 / tempF
		#tempF -= 273.15 # in Celcius
		#tempF = tempF*9.0/5.0+32.0
		#return tempF		

#discard all the packets waiting to be read
while xbee.receive():
	discard = xbee.receive()

#define all the objects
Pump = pump()
P = pressureTransducer()
T = thermistor()
sol = solenoid()

#how to use the objects
Pump.turnOn()
time.sleep(5) #wait some seconds to pressurize the system
print(P.psi())
print(T.F())
sol.pressurize()
time.sleep(2)
print(P.psi())
sol.depressurize()
time.sleep(1)
Pump.turnOff()


#xbee.transmit(EndDevice1,'I am ready'+ '\r\n')
def read():
	while True:
		p = xbee.receive()
		if p:
			print(p['payload'])
			start = time.ticks_ms()
			payloadT = str(T.readRawADCTemperature())
			payloadP = str(P.readRawADCPressure())
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

read()

