# Source - https://stackoverflow.com/questions/7546050/switch-between-two-frames-in-tkinter/7557028#7557028
# Posted by Bryan Oakley, modified by community. See post 'Timeline' for change history
# Retrieved 2025-12-27, License - CC BY-SA 4.0


import tkinter as tk                # python 3
from tkinter import font as tkfont  # python 3
from tkinter import filedialog as fd
from utils import *


class App(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title_font = tkfont.Font(
            family='Helvetica', size=18, weight="bold", slant="italic")

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, PageOne, PageTwo):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="File Encrypt/Decrypt Tool by Purinat33",
                         font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)

        button1 = tk.Button(self, text="Encrypt File",
                            command=lambda: controller.show_frame("PageOne"))
        button2 = tk.Button(self, text="Decrypt File",
                            command=lambda: controller.show_frame("PageTwo"))
        button1.pack()
        button2.pack()


# Encrypt File
class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Encrypt a File",
                         font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        button = tk.Button(self, text="Go to the start page",
                           command=lambda: controller.show_frame("StartPage"))
        button.pack()
        # User select a file and everything work the same
        # https://www.pythontutorial.net/tkinter/tkinter-open-file-dialog/
        self.file_button = tk.Button(
            self, text="Select File for Encryption", command=self.select_file)
        self.file_button.pack(expand=True)

    def select_file(self):
        file_types = (
            ('text files', '*.txt'),
            ("All Files", "*.*")
        )
        self.file = fd.askopenfilename(
            title="Open a File",
            initialdir='/',
            filetypes=file_types
        )

        self.file_label = tk.Label(self, text=f"File Opened: {self.file}")
        self.file_label.pack()

        self.password_label = tk.Label(self, text=f"Input Password Here")
        self.password_label.pack()

        self.password_field = tk.Entry(self, show='*', width=64)
        self.password_field.pack()

        self.encrypt_button = tk.Button(
            self, text="Encrypt", command=lambda: encrypt(self.file, self.password_field.get()))
        self.encrypt_button.pack()

# Decrypt File
class PageTwo(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Decrypt a File",
                         font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        button = tk.Button(self, text="Go to the start page",
                           command=lambda: controller.show_frame("StartPage"))
        button.pack()
        self.file_button = tk.Button(
            self, text="Select File for Decryption", command=self.select_file)
        self.file_button.pack(expand=True)

    def select_file(self):
        file_types = (
            ('Encrypted files', '*.enc'),
            ("All Files", "*.*")
        )
        self.file = fd.askopenfilename(
            title="Open a File",
            initialdir='encrypted/',
            filetypes=file_types
        )

        self.file_label = tk.Label(self, text=f"File Opened: {self.file}")
        self.file_label.pack()

        self.password_label = tk.Label(self, text=f"Input Password Here")
        self.password_label.pack()

        self.password_field = tk.Entry(self, show='*', width=64)
        self.password_field.pack()

        self.encrypt_button = tk.Button(
            self, text="Decrypt", command=lambda: decrypt(self.file, self.password_field.get()))
        self.encrypt_button.pack()
        
