from tkinter import *
from tkinter import ttk
from digi.xbee.devices import Raw802Device, RemoteRaw802Device,XBee16BitAddress
import time
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg #, NavigationToolbar2TkAgg
import os
import numpy as np
import threading
from queue import Queue

class Root(Tk):
    def __init__(self):
        super(Root, self).__init__()
        self.title("Cycle Tester")
        self.minsize(500,200)
        self.configure(background = '#3CD677')
        
        ttk.Style().configure("TLabel", padding=6, relief="flat", background="#3CD677")
        
        self.status = StringVar()
        self.status.set('Ready...')
        
        self.onButton = ttk.Button(self, text = "Pump On" , command = self.On)
        self.portLabel = ttk.Label(self, text = "Port: ")
        self.port = ttk.Entry(self)
        self.fileLabel = ttk.Label(self, text = "Filename: ")
        self.file = ttk.Entry(self)
        self.durationLabel = ttk.Label(self, text = "Cycle duration (s): ", justify=RIGHT)
        self.duration = ttk.Entry(self, justify=LEFT)
        self.numPointsLabel = ttk.Label(self, text = "Points in 1 cycle: ", justify=RIGHT)
        self.numPoints = ttk.Entry(self, justify=LEFT)
        self.acceptableErrorLabel = ttk.Label(self, text = "Acceptable Error: ", justify=RIGHT)
        self.acceprableError = ttk.Entry(self, justify=LEFT)
        self.numOfCyclesLabel = ttk.Label(self, text = "Number of cycles: ", anchor='e', justify = 'right')
        self.numOfCycles = ttk.Entry(self)
        self.offButton = ttk.Button(self, text = "Pump Off", command = self.Off)
        self.runButton = ttk.Button(self, text = "Run", command = self.r)
        self.stateLabel = ttk.Label(self, textvariable = self.status)
              
        self.portLabel.grid(column = 10 , row = 10 , sticky = E, padx = 2)
        self.port.grid(column = 11, row = 10)
        self.fileLabel.grid(column = 10 , row = 11 , sticky = E, padx = 2)
        self.file.grid(column = 11, row = 11)
        self.durationLabel.grid(column = 10, row = 12 , sticky = E, padx = 2)
        self.duration.grid(column = 11,row = 12 )
        self.numPointsLabel.grid(column = 10, row = 13 , sticky = E, padx = 2)
        self.numPoints.grid(column = 11,row = 13 )
        self.acceptableErrorLabel.grid(column=10,row=14 , sticky = E, padx = 2)
        self.acceprableError.grid(column=11,row=14)
        self.numOfCyclesLabel.grid(column=10,row=15 , sticky = E, padx = 2)
        self.numOfCycles.grid(column =11,row=15)
        self.runButton.grid(column=10,row=26, padx = 5, pady = 5, columnspan = 2)
        self.onButton.grid(column = 10, row = 25, padx = 5, pady = 5, columnspan = 2) 
        self.offButton.grid(column=10,row=24, padx = 5, pady = 5, columnspan = 2)
        self.stateLabel.grid(column =10, row = 27, padx = 5, pady = 5, columnspan=2)
        
        
        #self.coordinator = Raw802Device("COM29", 115200)
        self.endDeviceAddress = XBee16BitAddress.from_hex_string("EEEE")
        self.fileName = "TestData.csv"
        self.cycleDuration = 10000 # in milliseconds
        self.ADCFluctuations = 20 # 20 ADC readings out of 4096
        self.numberOfPoints = 20 # number of pressure readings in one cycleDuration
        self.numberOfCycles = 50
        self.timeBetweenCycles = 1
        self.completedCycles = 0
        self.comPort = "COM1"
        self.onHold = False
        self.pressureData = Queue()
        self.pressureData.put(np.asarray([0,1,2,3,4,5,6,7,8,9]))
        self.timeData = Queue()
        self.timeData.put(np.asarray([0,1,2,3,4,5,6,7,8,9]))
		
        self.fig = Figure(figsize=(6,4), dpi =100)
        self.a = self.fig.add_subplot(111)
        self.a.set_xlabel("time (s)")
        self.a.set_ylabel("pressure (psi)")
        self.a.set_title("Pressure variations during the last cycle")
        self.a.grid(visible = True)
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().grid(column = 12, row = 10, columnspan = 3, rowspan = 30, padx = 10, pady = 10)
        self.canvas.draw()
        
        
        self.updateGraph() # initial call, it will call itself every some time
    
    def On(self):
        try:
            if self.onHold == False:
                self.status.set('Busy...')
                self.onHold = True
                self.cycleDuration = int(self.duration.get())*1000
                self.ADCFluctuations = int(self.acceprableError.get())
                self.numberOfPoints = int(self.numPoints.get())
                self.numberOfCycles = int(self.numOfCycles.get())
                self.fileName = str(self.file.get())
                self.comPort = str(self.port.get())
                o = threading.Thread(target = self.turnPumpOn)
                o.start()
        except Exception as e:
            print(e)
            self.onHold = False
            self.status.set("Ready...")
    
    def Off(self):
        try:
            if self.onHold == False:
                self.status.set('Busy...')
                self.onHold = True
                self.cycleDuration = int(self.duration.get())*1000
                self.ADCFluctuations = int(self.acceprableError.get())
                self.numberOfPoints = int(self.numPoints.get())
                self.numberOfCycles = int(self.numOfCycles.get())
                self.fileName = str(self.file.get())
                self.comPort = str(self.port.get())
                off = threading.Thread(target = self.turnPumpOff)
                off.start()
        except Exception as e:
            print(e)
            self.onHold = False
            self.status.set("Ready...")
        
    def r(self):
        try:
            if self.onHold == False:
                self.status.set('Busy...')
                self.onHold == True
                self.cycleDuration = int(self.duration.get())*1000
                self.ADCFluctuations = int(self.acceprableError.get())
                self.numberOfPoints = int(self.numPoints.get())
                self.numberOfCycles = int(self.numOfCycles.get())
                self.fileName = str(self.file.get())
                self.comPort = str(self.port.get())
                rr = threading.Thread(target = self.run)
                rr.start()
        except Exception as e:
            print(e)
            self.onHold = False
            self.status.set("Ready...")
    
    def runOneCylceCommand(self):
        command = "C " + str(self.cycleDuration) + " " + str(self.ADCFluctuations)+ " " + str(self.numberOfPoints)
        return command
    
    def readData(self, message, filename):
        reading = True
        try:
            if os.path.exists(self.fileName):
                append_write = 'a'
            else:
                append_write = 'w'
            f = open(self.fileName, append_write)
            if message not in ["I","O"]:
                f.write(str(self.completedCycles+1) + ',')
            while reading:
                xbee_message = self.coordinator.read_data()
                if xbee_message is not None:
                    reading = False
                    f.write("%s" % (xbee_message.data.decode()))
            f.write("\n")
            f.close()
        except Exception as e: 
            print(e)
        
    def turnPumpOn(self):
        command = "I"
        try:
            self.coordinator = Raw802Device(self.comPort, 115200)
            self.coordinator.open()
            self.coordinator.send_data_16(self.endDeviceAddress, command)
            self.readData(command, self.fileName)
            #time.sleep(0.5)
        except Exception as e: 
            print(e)
        finally:
            if self.coordinator is not None and self.coordinator.is_open():
                self.coordinator.close()
                self.onHold = False
            self.status.set('Ready...')
            
    def turnPumpOff(self):
        command = "O"
        try:
            self.coordinator = Raw802Device(self.comPort, 115200)
            self.coordinator.open()
            self.coordinator.send_data_16(self.endDeviceAddress, command)
            self.readData(command, self.fileName)
        except Exception as e: 
            print(e)
        finally:
            if self.coordinator is not None and self.coordinator.is_open():
                self.coordinator.close()
                self.onHold = False
            self.status.set('Ready...')
            
    def runOneCycle(self):
        command = self.runOneCylceCommand()
        try:
            self.coordinator.send_data_16(self.endDeviceAddress, command)
            self.readData(command, self.fileName)
        except Exception as e: 
            print(e)
        finally:
            pass
            #if self.coordinator is not None and self.coordinator.is_open():
            #    self.coordinator.close()
            
    def runAllCycles(self):
        try:
            self.completedCycles = 0
            #self.turnPumpOn() #the user should turn the pump on
            #time.sleep(4)
            self.coordinator = Raw802Device(self.comPort, 115200)
            self.coordinator.open()
            for i in range(self.numberOfCycles):
                self.runOneCycle()
                self.completedCycles = i+1
                self.updatePlot()
	
            self.coordinator.close()
            self.turnPumpOff()
        except Exception as e: 
            print(e)
        finally:
            if self.coordinator is not None and self.coordinator.is_open():
                self.coordinator.close()
    
    def run(self):
        try:
            self.runAllCycles()
        except Exception as e: 
            print(e)
        finally:
            self.onHold = False
            self.status.set('Ready...')
        
    def updatePlot(self):
        try:
            #self.a.clear()
            with open(self.fileName, 'rb') as f:
                f.seek(-2, os.SEEK_END)
                while f.read(1) != b'\n':
                    f.seek(-2, os.SEEK_CUR) 
                last_line = f.readline().decode()
                dataPoints = [int(e) if e.isdigit() else e for e in last_line.split(',')]
                dataPoints = np.asarray(dataPoints, dtype=np.float32)
                pressureData = 409.09*(dataPoints[2:-1]* 3.3 / 4096)-130.91
                timeData = np.linspace(0.0,self.cycleDuration, self.numberOfPoints)
            
            self.timeData.put(timeData)
            self.pressureData.put(pressureData)
            print(pressureData)
        except Exception as e: 
            print(e)
            
    def updateGraph(self):
        print("updateGraph called")
        if not self.pressureData.empty():#if updatePlot function has put some pressure data in the queue
            self.a.clear()#need to check if this works as expected
            self.a.set_xlabel("time (s)")
            self.a.set_ylabel("pressure (psi)")
            self.a.set_title("Pressure variations during the last cycle")
            self.a.grid(visible = True)
            self.canvas.draw()
            self.a.grid(visible = True)
            self.a.plot(self.timeData.get()/1000,self.pressureData.get(),label = str(self.completedCycles))
            self.a.legend()
            self.canvas.draw()
        self.after(2000, self.updateGraph) #calls itself periodically to see if there is new pressure data available to plot

root = Root()
root.mainloop()
