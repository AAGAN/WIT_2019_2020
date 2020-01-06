from digi.xbee.devices import Raw802Device, RemoteRaw802Device,XBee16BitAddress
import time

coordinator = Raw802Device("COM29", 115200)
#endDevice = RemoteRaw802Device(coordinator,XBee16BitAddress.from_hex_string("EEEE")) #remote must be in api mode
NEW_TIMEOUT_FOR_SYNC_OPERATIONS = 5 # 5 seconds

def readData():
    reading = True
    while reading:
        xbee_message = coordinator.read_data()
        if xbee_message is not None:
            reading = False
            print("From %s >> %s" % (xbee_message.remote_device.get_64bit_addr(),xbee_message.data.decode()))

try:
    coordinator.open()
    endDeviceAddress = XBee16BitAddress.from_hex_string("EEEE")
    #coordinator.reset() #software resets the xbee if it is not acting normal, can be applied to the remote xbee
    #endDevice.reset()
    
    coordinator.send_data_16(endDeviceAddress, "I") #turns on the pump
    readData()
    time.sleep(2)
    coordinator.send_data_16(endDeviceAddress, "C 1000 2 50")# runs one cycle with 1000ms duration, 2ADC fluctuations and 30 points
    readData()
    time.sleep(2)
    coordinator.send_data_16(endDeviceAddress, "O") #turns off the pump
    readData()
    time.sleep(2)
    
    
    
finally:
    if coordinator is not None and coordinator.is_open():
        coordinator.close()
