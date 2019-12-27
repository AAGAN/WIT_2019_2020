import xbee

xbee = Raw802Device("COM1", 115200)
#remote_xbee = RemoteRaw802Device(xbee,Xbee64BitAddress.from_hex_string("0013A200ffffffff") #remote must be in api mode
