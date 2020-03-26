from MouseArduino import MouseArduino
import threading
import time

baudrate = 115200
stopReward = threading.Event()
def oneReward(ard):
    while not stopReward.is_set():
        ard.reset_input_buffer()
        ard.deliverReward()
        time.sleep(0.1)

def main(comPort,ard):
    if ard == False:
        ports=MouseArduino.listOpenPorts()
        port = None
        for p in ports:
            if "USB Serial Port" in p.description and all([x not in p.description for x in ["Keyspan", "Teensy"]]):
                port = p
                print("Port found: {}".format(p))
        if port is None:
            print("Port not found")
            input("Press Enter to quit")
            return
        ard = MouseArduino(port.device,baudrate)
    t = threading.Thread(target=oneReward,args=[ard])
    ans = input("Press enter to start drain(q to stop)")
    if ans == 'q':
        return
    t.start()
    print("DRAINING")
    input("Press enter to stop")
    stopReward.set()
    t.join()
    stopReward.clear()
    main(comPort,ard)

    
    

if __name__ == "__main__":
    main(False,False)
    
        

