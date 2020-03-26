import os,sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0,parent_dir)

import os
import logging
import threading
from MouseArduino import MouseArduino

TRACK_NAMES = ["Linear"]
data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'BehavioralData')

class Session(object):
    def __init__(self, io: MouseArduino, session_name: str = None, session_number: str = None, recording = False):
        self.io = io
        self.io.start()
        self.recording = recording

        self.session_name = session_name
        self.session_number = session_number
        self.track_name = TRACK_NAMES[0]
        self.session_time = 0
        self.file_name = "{}_{}_{}.txt".format(session_name, self.track_name, session_number)
        if self.recording:
            if not (os.path.exists(data_path)):
                os.makedirs(data_path)
        self.thread = threading.Thread(target=self.receive_data)
        self.thread.start()

        self.reward_count = 0
        self.lick_count = 0
        self.shock_count = 0
        self.spike_count = 0

        self.send_string = ""
        self.session_time = 0
        self.data = []

        self.initialize = True

    def deliver_shock(self):
        self.shock_count += 1
        self.io.deliverShock()

    def deliver_reward(self):
        self.reward_count += 1
        self.io.deliverReward()

    def receive_data(self):
        print(self.io.newMsg.is_set())
        if self.io.newMsg.is_set():
            print("******RECEIVING DATA******")
            self.io.newMsg.clear()
            string_data = self.io.msgQueue.get()

            if self.recording:
                with open(os.path.join(data_path, self.file_name), "w+") as f:
                    f.write(string_data + "\n")

            data_args = string_data.split(',')

            if len(data_args >= 2):
                Bevt = data_args[1] # 2-letter descriptor of behavioral event
                print("Bevt = {}".format(Bevt))
            else:
                Bevt = "NULL"
                logging.warning("Data received has less than 2 arguments.")

            if Bevt == "VR":
                BC_tstamp, Bevt, vr_time, vr_x, vr_y, vr_z, vr_speed, vr_dir, eventCnt, eventstr_1, eventstr_2 = data_args
                self.session_time = round(int(vr_time) / 1000)

            if Bevt == "LK":
                self.lick_count += 1

            if Bevt == "RD":
                self.reward_count += 1

            if Bevt == "TH":
                self.spike_count += 1

            if self.initialize:
                self.io.write('speed_th_tag 0\r')
                self.io.write('speed_th 4000\r')
                self.io.write('moveto 1 0 \r')
                self.io.write('videoRecON\r')
                self.initialize = False

        # if ard.newMsg.is_set():
        #     ard.newMsg.clear()
        #     while ard.msgQueue.isnotempty():
        #         ard.msgQueue.get()


        # with open(os.getcwd() + "\\" + self.file_name, "w+") as f:
        #     recording = True
        #     while recording:
        #         while not self.io.msgQueue.empty():
        #             stringStored = self.io.msgQueue.get()
        #             f.write(stringStored)
        #
        #             BC_tstamp, Bevt, vr_time, vr_x, vr_y, vr_z, vr_speed, vr_dir, eventCnt, eventstr_1, eventstr_2, eventstr_3, eventstr_4 = stringStored.split(',')
        #             self.data.append(stringStored.split(","))
