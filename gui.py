from tkinter import *
from tkinter import ttk
from tkinter import font as tkfont

# https://stackoverflow.com/questions/7546050/switch-between-two-frames-in-tkinter/7557028#7557028


class App(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)

        container = Frame(self)
        container.pack(side='top', fill='both', expand=True)
