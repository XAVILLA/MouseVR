import queue
import threading
""" 
keyboard input reader to replace arduino.
Testing purpose
"""
class Keyboard:
    def __init__(self,eventOnly=False):
        self.msgQueue = queue.Queue() 
        self.reader  = None
        self.newMsg = threading.Event() 
        self.stopWait = threading.Event() 
        self.eventOnly = eventOnly

    def start(self):
        self.stop()
        self.reader = threading.Thread(target=self.threadStartReading)
        self.reader.start()
            
    def stop(self):
        if self.reader and self.reader.is_alive():
            self.stopWait.set()
            self.reader.join()
            self.stopWait.clear()
            return True
        return False

    def threadStartReading(self):
        while not self.stopWait.is_set():
            strmsg = self.readline()
            if strmsg:
                if not self.eventOnly:
                    logging.debug("New Message from Hardware: {}".format(strmsg))
                    self.msgQueue.put(strmsg)
                self.newMsg.set()

    def readline(self):
        input("Press Enter to send LK")
        self.msgQueue.put("0,LK")
        self.newMsg.set()

    def write(self,strOutput):
        print("Sending {} signal to hardware".format(strOutput))

    def stopReading(self):
        self.stopWait.set()
        

    def deliverReward(self):
        self.write("reward")

    def getTime(self):
        self.write("timestamp")

    def clearQueue(self):
        self.msgQueue = queue.Queue()

    def startPump(self):
        logging.info("PUMP ON")
        self.write("startpump")

    def stopPump(self):
        logging.info("PUMP OFF")
        self.write("stoppump")

    def clearQueue(self):
        if not self.eventOnly:
            self.msgQueue = queue.Queue()
        self.newMsg.clear()

    def isAlive(self):
        return self.reader.isAlive()
    def getUnoPort():
        return "KEYBOARD DEBUGGER"

    def listOpenPorts():
        return serial.tools.list_ports.comports()
    def reset_input_buffer(self):
        print("Hardware input buffer reset")


