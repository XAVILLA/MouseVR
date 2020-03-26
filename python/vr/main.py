from utils import *
from session import Session
from MouseArduino import MouseArduino
from gui import Gui
from tkinter import Tk


def main():
    # Session
    serialIO = MouseArduino(comPort="COM8", baudrate=115200)
    session = Session(io=serialIO, session_name="666666", session_number="2019111201")
    session.run()

    # GUI
    root = Tk()
    root.title("MouseVR")
    root.geometry("1200x800")
    gui = Gui(root)
    gui.run()

if __name__ == '__main__':
    main()







