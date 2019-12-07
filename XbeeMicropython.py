import xbee
import machine
import time

pressurePin = machine.ADC('D1')

temperaturePin = machine.ADC('D0')

pumpPinOn = machine.Pin.board.D2
pumpPinOff = machine.Pin.board.D3
pumpPinOn.mode(machine.Pin.OUT)
pumpPinOff.mode(machine.Pin.OUT)
pumpPinOff.value(1)
pumpPinOn.value(0)

solenoidPin = machine.Pin.board.D4
solenoidPin.mode(machine.Pin.OUT)
solenoidPin.value(0)

Coordinator = b'\x00\x13\xa2\x00\x41\x93\xf6\x4b' 
EndDevice1  = b'\x00\x13\xa2\x00\x41\x92\xcd\xf3'
EndDevice2  = b'\x00\x13\xa2\x00\x41\x95\xce\x13'
EndDevice3  = b'\x00\x13\xa2\x00\x41\x92\xdc\x03'

#discard all the packets waiting to be read
while xbee.receive():
	discard = xbee.receive()
	
xbee.transmit(EndDevice1,'I am ready'+ '\r\n')
def read():
	while True:
		p = xbee.receive()
		if p:
			start = time.ticks_ms()
			payload1 = str(pressurePin.read())
			payload2 = p['payload'].decode('UTF-8')
			#print(payload1)
			xbee.transmit(EndDevice,50 * (payload1 +' ')+ '\r\n')
			#xbee.transmit(EndDevice,payload1 + '\r\n')
			solenoidPin.toggle()
			print(time.ticks_diff(time.ticks_ms(), start))

read()

witEndDevice   = b'\x00\x13\xa2\x00\x41\x98\x49\xde'
witCoordinator = b'\x00\x13\xa2\x00\x41\x97\xff\x02' #or just 0 would work too
