import xbee

coordinator = Raw802Device("COM1", 115200)
endDevice = RemoteRaw802Device(coordinator,Xbee16BitAddress.from_hex_str("00E1") #remote must be in api mode
NEW_TIMEOUT_FOR_SYNC_OPERATIONS = 5 # 5 seconds
                               
try:
  coordinator.open()
  
  #coordinator.reset() #software resets the xbee if it is not acting normal, can be applied to the remote xbee
  #endDevice.reset()
                               
  coordinator.send_data_16(endDevice, "Hello endDevice")#waits 2 seconds for timeout
  print("Current timeout: %d seconds" % coordinator.get_sync_ops_timeout())
  coordinator.set_sync_ops_timeout(NEW_TIMEOUT_FOR_SYNC_OPERATIONS)

finally:
  if coordinator is not None and coordinator.is_open():
    coordinator.close()
