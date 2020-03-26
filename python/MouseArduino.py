import serial
import serial.tools.list_ports
import queue
import threading
import logging
import queue
import time
"""
I/O for Arduino or BCS
Start waiting by using self.start()
Make sure to self.stop() if you want to create another instance of MouseArduino since comport can't be opened simultaneously
Message will arrive in self.msgQueue and self.newMsg event will be set(make sure to clear() afterwards)
"""
class MouseArduino:
    def __init__(self,comPort,baudrate,eventOnly = False,readTimeout=1):
        
        self.arduino = None
        self.reader  = None
        self.comPort = comPort
        self.baudrate = baudrate
        self.timeout = readTimeout
        self.msgQueue = queue.Queue() #Messages received from arduino. 
        self.newMsg = threading.Event() #Will be sent when new message is received from arduino
        self.stopWait = threading.Event() #Stop reading arduino messages
        self.eventOnly = eventOnly

    """
    Opens port and start reading. Messages will be delivered to self.msgQueue and self.newMsg will be set
    """
    def start(self):
        self.stop()
        try:
            self.arduino = serial.Serial(self.comPort,self.baudrate,timeout=self.timeout)
            self.reader = threading.Thread(target=self.threadStartReading)
            self.reader.start()
            #Wait for init success message
            if self.newMsg.wait(5):
                if self.eventOnly:
                    self.write('quiet')
                else:
                    self.write('verbose')
            else:
                raise Exception('Arduino initialization failed')
        except Exception as e:
            raise Exception("{} Make sure other programs like arduino or Matlab isn't running and grabbing the port".format(e))

    """
    Stops reading and closes port. msgQueue will NOT be cleared
    """
    def stop(self):
        if self.arduino:
            if self.reader.is_alive():
                self.stopWait.set()
                self.reader.join()
            if self.arduino.isOpen():
                self.arduino.close()
            self.stopWait.clear()
            return True
        return False
        

    """
    Unless stopWait event is set, it'll continuously wait for arduino string messages and put it in msgQueue.
    """
    def threadStartReading(self):
        while not self.stopWait.is_set():
            strmsg = self.readline()
            if strmsg:
                if not self.eventOnly:
                    logging.debug("New Message from Hardware: {}".format(strmsg))
                    self.msgQueue.put(strmsg)
                self.newMsg.set()

    def readline(self):
        return self.arduino.readline().decode('utf-8')

    """
    Write to Arduino ex) "reward","timestamp"
    """
    def write(self,strOutput):
        self.arduino.write((strOutput+"\r").encode()) 
    

    def deliverReward(self):
        logging.info("REWARD")
        self.write("reward")

    def deliverShock(self):
        logging.info("SHOCK")
        self.write("shock")

    """
    Turns off automatically after 5 seconds
    Implemented only in AppleBanana arduino for now
    """
    def startPump(self):
        logging.info("PUMP ON")
        self.write("startpump")

    def stopPump(self):
        logging.info("PUMP OFF")
        self.write("stoppump")

    def getTime(self):
        self.write("timestamp")

    def clearQueue(self):
        if not self.eventOnly:
            self.msgQueue = queue.Queue()
        self.newMsg.clear()

    def isAlive(self):
        return self.reader.isAlive()

    """
    Try to find port device with name 'Arduino Uno' and return string value of its comport. 
    error string is returned if not found or duplicate is found
    """
    @staticmethod
    def getUnoPort():
        ports = MouseArduino.listOpenPorts()
        port = None
        for p in ports:
            if 'Arduino Uno' in p.description and all([x not in p.description for x in ["Keyspan", "Teensy"]]):
                if port != None:
                    port = 'Several Arduino Unos found. Enter Comport manually'
                else:
                    port = p.device
        if port is None:
            port = "Arduino Uno Not Found"
        return port

    """
    List of open ports
    """
    @staticmethod
    def listOpenPorts():
        return serial.tools.list_ports.comports()

    """
    Flush input buffer
    """
    def reset_input_buffer(self):
        self.arduino.reset_input_buffer()
