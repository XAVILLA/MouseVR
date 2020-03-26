import logging
from tkinter import *
from utils import get_date
from session import Session
from MouseArduino import MouseArduino

LARGE_FONT = ("Verdana", 14)
# BACKGROUND_COLOR = '#f0f0f0'
BACKGROUND_COLOR = '#ced8e1'
# BACKGROUND_COLOR = '#ffffff'
# BACKGROUND_COLOR = '#F7F7F2'
HEADER_COLOR = '#112b3d'
LABEL_COLOR = '#2cc7a0'

COMPORT = "/dev/cu.Bluetooth-Incoming-Port"
BAUDRATE = 115200

class Gui():
    def __init__(self, master: Tk):
        self.master = master
        self.master.configure(background=BACKGROUND_COLOR)
        self.ard = MouseArduino(comPort=COMPORT, baudrate=BAUDRATE)
        self.session = Session(io=self.ard)
        self.is_recording = False

        # FRAMES
        self.container = Frame(master, bg=BACKGROUND_COLOR)
        self.container.pack(side="top", fill="both", expand = True, padx=20, pady = 20)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_rowconfigure(1, weight=1)
        self.container.grid_rowconfigure(2, weight=4)
        self.container.grid_columnconfigure(0, weigh=1, uniform='column_group')
        self.container.grid_columnconfigure(1, weigh=1, uniform='column_group')

        self.session_info_frame = Frame(self.container, bg=BACKGROUND_COLOR, bd=3, relief="raised")
        self.session_info_frame.grid(row=0, column=0, sticky="nsew")
        self.recording_control_frame = Frame(self.container, bg=BACKGROUND_COLOR, bd=3, relief="raised")
        self.recording_control_frame.grid(row=0, column=1, sticky="nsew")
        self.reward_system_frame = Frame(self.container, bg=BACKGROUND_COLOR, bd=3, relief="raised")
        self.reward_system_frame.grid(row=1, column=0, sticky = "nsew")
        self.punish_system_frame = Frame(self.container, bg=BACKGROUND_COLOR, bd=3, relief="raised")
        self.punish_system_frame.grid(row=1, column=1, sticky = "nsew")

        # Session Information
        self.session_info_label = Label(self.session_info_frame, text="Session Information", width=50,
                                   borderwidth=2, relief="solid", font=LARGE_FONT, bg=HEADER_COLOR, fg='white')
        self.session_info_label.grid(row = 0, columnspan=2, padx=40, pady=10)

        self.session_name_label = Label(self.session_info_frame, text="Mouse Number: ", width=20, bg=LABEL_COLOR)
        self.session_name_label.grid(row=1, column=0, pady=(10, 0), padx=(3, 0))
        self.session_name = Entry(self.session_info_frame)
        self.session_name.insert(0, "000000")
        self.session_name.grid(row=1, column=1, pady=(10, 0))

        self.date_number_label = Label(self.session_info_frame, text="Date + Session Number:", width=20, bg=LABEL_COLOR)
        self.date_number_label.grid(row=2, column=0, pady = (10, 0), padx=(3, 0))
        self.date_number = Entry(self.session_info_frame)
        self.date_number.insert(0, get_date() + "01")
        self.date_number.grid(row=2, column=1, pady=(10, 0))

        self.session_time_label = Label(self.session_info_frame, text="Session Time (sec):", relief="flat",
                                        bg=BACKGROUND_COLOR)
        self.session_time_label.grid(row=3, column=0, pady = (20, 0), padx=(0, 50))
        self.session_time_var = IntVar()
        self.session_time_var.set(self.session.session_time)
        self.session_time = Label(self.session_info_frame, textvariable=self.session_time_var, relief="sunken", width=5,
                                  bg=BACKGROUND_COLOR)
        self.session_time.grid(row=3, pady=(20,0), padx=(140, 0))

        # Recording Control
        self.recording_label = Label(self.recording_control_frame, text="Recording Control", width=50,
                                   borderwidth=2, relief="solid", font=LARGE_FONT, bg=HEADER_COLOR, fg='white')
        self.recording_label.grid(row = 0, columnspan=2, padx=(57, 0), pady=10)

        self.recording_button = Button(self.recording_control_frame, text="Recording OFF", width=20, height=2,
                                       command=self.toggle_recording_session)
        self.recording_button.grid(row=1, column=0, padx = (30, 0), pady = 10)
        self.pause_button = Button(self.recording_control_frame, text="Pause OFF", width=20, height=2,
                                   command=self.toggle_pause_session)
        self.pause_button.grid(row=1, column=1, sticky="e")

        self.port_reset_button = Button(self.recording_control_frame, text="Serial Port Reset", width=30, height=1)
        self.port_reset_button.grid(row=2, columnspan=2, pady = (10, 0), padx=(50, 0))

        self.send_string_label = Label(self.recording_control_frame, text="Send String:", bg=LABEL_COLOR, width=10)
        self.send_string_label.grid(row=3, column=0, pady=(30, 0), padx=(30, 0), sticky="w")
        self.send_string = Entry(self.recording_control_frame, width=40)
        self.send_string.grid(row=3, columnspan=2, pady=(30, 0), padx=(140, 0))
        self.send_string.bind("<Return>", lambda event: self.send_string.delete(0, "end"))

        # Reward System
        self.reward_sys_label = Label(self.reward_system_frame, text="Reward System", width=50,
                                      borderwidth=2, relief="solid", font=LARGE_FONT, bg=HEADER_COLOR, fg='white')
        self.reward_sys_label.grid(row=0, columnspan=2, padx=(40, 0), pady=(20, 0))

        self.reward_label = Label(self.reward_system_frame, text="Rewards:", bg=LABEL_COLOR, width=20)
        self.reward_label.grid(row=1, column=0, pady=20, padx=(60, 0))
        self.reward_count_var = IntVar()
        self.reward_count_var.set(self.session.reward_count)
        self.reward_count = Label(self.reward_system_frame, textvariable=self.reward_count_var, width=10, bg="yellow",
                                  relief="raised")
        self.reward_count.grid(row=1, column=1, pady=20, padx=(0, 80))

        self.licks_label = Label(self.reward_system_frame, text="Licks:", bg=LABEL_COLOR, width=20)
        self.licks_label.grid(row=2, column=0, padx=(60, 0))
        self.lick_count_var = IntVar()
        self.lick_count_var.set(self.session.lick_count)
        self.lick_count = Label(self.reward_system_frame, textvariable=self.lick_count_var, width=10, bg="yellow",
                                relief="raised")
        self.lick_count.grid(row=2, column=1, padx=(0, 80))

        self.reward_button = Button(self.reward_system_frame, text="Deliver Reward", width=20, height=2, bg="green",
                                    command=self.deliver_reward)
        self.reward_button.grid(row=3, columnspan=2, pady=25)

        # Punishment System
        self.punish_sys_label = Label(self.punish_system_frame, text="Punishment System", width=50,
                                      borderwidth=2, relief="solid", font=LARGE_FONT, bg=HEADER_COLOR, fg='white')
        self.punish_sys_label.grid(row=0, columnspan=2, padx=(57, 0), pady=(20, 0))

        self.shock_label = Label(self.punish_system_frame, text="Shocks:", bg=LABEL_COLOR, width=20)
        self.shock_label.grid(row=1, column=0, pady=40, padx=(90, 0))
        self.shock_count_var = IntVar()
        self.shock_count_var.set(self.session.shock_count)
        self.shock_count = Label(self.punish_system_frame, textvariable=self.shock_count_var, width=10, bg="yellow",
                                 relief="raised")
        self.shock_count.grid(row=1, column=1, pady=20, padx=(0, 60))

        self.shock_button = Button(self.punish_system_frame, text="Deliver Shock", width=20, height=2, bg='red',
                                   command=self.deliver_shock)
        self.shock_button.grid(row=3, columnspan=2, padx=(70, 0))

        """ To remove the caret/cursor from Entry elements when clicked outside the entry box"""
        self.session_info_frame.bind("<Button-1>", lambda event: self.master.focus())
        self.recording_control_frame.bind("<Button-1>", lambda event: self.master.focus())
        self.reward_system_frame.bind("<Button-1>", lambda event: self.master.focus())
        self.punish_system_frame.bind("<Button-1>", lambda event: self.master.focus())
        self.container.bind("<Button-1>", lambda event: self.master.focus())

    def deliver_reward(self):
        if self.session:
            # self.reward_count["textvariable"] += 1
            # self.reward_count_var.set(self.reward_count_var.get() + 1)
            self.session.deliver_reward()
            self.update_label_texts()
        else:
            logging.warning("Session has not started yet.")

    def deliver_shock(self):
        if self.session:
            # self.shock_count["text"] += 1
            self.session.deliver_shock()
            self.update_label_texts()
        else:
            logging.warning("Session has not started yet.")

    def toggle_recording_session(self):
        # Start Recording Session
        if self.recording_button["text"] == "Recording OFF":
            self.ard = MouseArduino(comPort=COMPORT, baudrate=BAUDRATE)
            mouse_number = self.session_name.get()
            session_number = self.date_number.get()
            self.session = Session(io=self.ard, session_name=mouse_number, session_number=session_number, recording=True)
            self.update_label_texts()

            self.recording_button["text"] = "Recording ON"
            self.recording_button.config(bg="green")
            self.is_recording = True
        else:
            # Stop Recording Session
            self.recording_button["text"] = "Recording OFF"
            self.recording_button.config(bg="#f5f5f5")
            self.is_recording = False

    def toggle_pause_session(self):
        # Start Pausing Session
        if self.pause_button["text"] == "Pause OFF":
            self.pause_button["text"] = "Pause ON"
            self.pause_button.config(bg="red")
            self.is_recording = False
        else:
            # Stop Pausing Session
            self.pause_button["text"] = "Pause OFF"
            self.pause_button.config(bg="#f5f5f5")
            self.is_recording = False
            self.session = None

    def run(self):
        self.master.mainloop()

    def update_label_texts(self):
        self.reward_count_var.set(self.session.reward_count)
        self.shock_count_var.set(self.session.shock_count)
        self.lick_count_var.set(self.session.lick_count)


if __name__ == "__main__":
    root = Tk()
    root.title("MouseVR")
    root.geometry("1200x800")
    gui = Gui(root)
    gui.run()
    gui.session.io.stop()
