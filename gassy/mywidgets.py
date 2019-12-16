import tkinter as tk
from tkinter.messagebox import showerror, showinfo, showwarning, askyesno


main_font = ("Optima", 14)
header_font = ("Optima", 20)


class MyHeading(tk.Label):
    def __init__(self, *args, **kwargs):
        tk.Label.__init__(self, *args, **kwargs)
        self["font"] = header_font
        self["bg"] = "orange"


class MyButton(tk.Button):
    def __init__(self, *args, **kwargs):
        tk.Button.__init__(self, *args, **kwargs)
        self["font"] = main_font


class MyLabel(tk.Label):
    def __init__(self, *args, **kwargs):
        tk.Label.__init__(self, *args, **kwargs)
        self["font"] = main_font


class MyText(tk.Text):
    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)
        self["font"] = main_font
        self["relief"] = tk.GROOVE


class MyEntry(tk.Entry):
    def __init__(self, *args, **kwargs):
        tk.Entry.__init__(self, *args, **kwargs)
        self["font"] = main_font
        self["relief"] = tk.GROOVE


class MyCheckbutton(tk.Checkbutton):
    def __init__(self, *args, **kwargs):
        tk.Checkbutton.__init__(self, *args, **kwargs)
        self["font"] = main_font


class MyOptionMenu(tk.OptionMenu):
    def __init__(self, *args, **kwargs):
        tk.OptionMenu.__init__(self, *args, **kwargs)
        self.config(font=main_font)
        self["menu"].config(font=main_font)