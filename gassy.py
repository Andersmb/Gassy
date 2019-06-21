import tkinter as tk
import tkinter.messagebox
import numpy as np
import json
from pprint import pprint
import os
import datetime
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class Gassy(tk.Tk):
    """
    For embedding matplotlib in tk, see here:
    https://matplotlib.org/3.1.0/gallery/user_interfaces/embedding_in_tk_sgskip.html
    """
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.startup = True
        self.datafile = "/Users/Anders/Documents/github/Gassy/data.json"
        self.backupfile = "/Users/Anders/Documents/github/Gassy/.data_backup.json"

        try:
            with open(self.datafile) as f:
                self.data = json.load(f)
        except IOError:
            tk.messagebox.showwarning("Åtvaring", "Fyllingsdata ikkje funne!")

        self.mainwindow = MainWindow(self)
        self.show_main()
        self.startup = False

    def show_main(self):
        self.mainwindow.grid(row=0, column=0)
        if not self.startup:
            self.addnew.grid_forget()

    def show_addnew(self):
        self.addnew = AddNew(self)
        self.mainwindow.grid_forget()
        self.addnew.grid(row=0, column=0)


class MainWindow(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self)
        self.parent = parent

        label_title = tk.Label(self, text="Welcome to Gassy!", bg="orange")
        label_title.pack()

        tk.Button(self, text="Ny fylling...", command=self.register_new_fill).pack()
        tk.Button(self, text="Lukk", command=self.parent.destroy).pack()

    def plot_price(self):
        x = []
        y = []
        for entry in self.parent.data:
            x.append(entry["date"])
            y.append(entry["price"])

        fig = Figure()
        p_price = fig.add_subplot(111)

        p_price.scatter(x, y, marker="o", color="red", edgecolor="black")

        canvas = FigureCanvasTkAgg(fig, self)
        canvas.show()
        canvas.get_tk_widget().pack()

    def register_new_fill(self):
        self.parent.show_addnew()


class AddNew(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self)
        self.parent = parent
        self.bonus = tk.StringVar()
        self.bonus.set("Coop")
        self.station = tk.StringVar()
        self.station.set("Circle K")
        stations = ["Circle K", "Shell", "Best", "Uno-X", "Esso"]

        tk.Label(self, text="Legg til ny fylling").grid(row=0, column=0)
        self.entry_volume = tk.Entry(self)
        self.entry_price = tk.Entry(self)
        self.entry_date = tk.Entry(self)
        self.entry_time = tk.Entry(self)
        option_bonus = tk.OptionMenu(self, self.bonus, *["Coop", "Trumf", "Ingen bonus"])
        option_station = tk.OptionMenu(self, self.station, *stations)
        self.label_volume = tk.Label(self, text="Volum: ")
        self.label_price = tk.Label(self, text="Literpris: ")
        self.label_date = tk.Label(self, text="Dato: ")
        self.label_time = tk.Label(self, text="Klokkeslett: ")
        label_bonus = tk.Label(self, text="Bonusprogram: ")
        label_station = tk.Label(self, text="Stasjon: ")

        self.label_volume.grid(row=1, column=0, sticky=tk.E)
        self.label_price.grid(row=2, column=0, sticky=tk.E)
        self.label_date.grid(row=3, column=0, sticky=tk.E)
        self.label_time.grid(row=4, column=0, sticky=tk.E)
        label_bonus.grid(row=5, column=0, sticky=tk.E)
        label_station.grid(row=6, column=0, sticky=tk.E)
        self.entry_volume.grid(row=1, column=1, sticky=tk.W)
        self.entry_price.grid(row=2, column=1, sticky=tk.W)
        self.entry_date.grid(row=3, column=1, sticky=tk.W)
        self.entry_time.grid(row=4, column=1, sticky=tk.W)
        option_bonus.grid(row=5, column=1, sticky=tk.W)
        option_station.grid(row=6, column=1, sticky=tk.W)

        tk.Button(self, text="Lagre", command=self.append_new_fill).grid(row=7, column=0)
        tk.Button(self, text="Avbryt", command=self.parent.show_main).grid(row=8, column=0)
        tk.Button(self, text="Lukk", command=self.parent.destroy).grid(row=9, column=0)

        self.sanity_check()

    def append_new_fill(self):
        """
        Update the data file by appending the newly filled in information, if the information
        is in the correct format. If not, then show error message.
        :return:
        """
        if not VOL or not PRICE or not DATE or not TIME:
            tk.messagebox.showerror("Feilmelding", "Du har oppgitt verdiar i feil format.")
            return
        elif not tk.messagebox.askyesno("Åtvaring", "Er du sikker på at du vil leggje til ny fylling?"):
            return

        data = {}
        data["bonus"] = "False" if self.bonus.get() == "Ingen bonus" else self.bonus.get()
        data["station"] = self.station.get()
        data["volume"] = float(self.entry_volume.get())
        data["price"] = float(self.entry_price.get())
        data["time"] = self.entry_time.get()
        data["date"] = self.entry_date.get()

        with open(self.parent.backupfile, "w") as backupdata:
            json.dump(self.parent.data, backupdata, indent=4)

        with open(self.parent.datafile, "w") as maindata:
            self.parent.data.append(data)
            json.dump(self.parent.data, maindata, indent=4)

        tk.messagebox.showinfo("Gassy", "Ny fylling lagt til!")

    def sanity_check(self):
        """
        Evaluate whether the information provided in Entries are valid.
        Continuously monitor whether the criteria are fulfilled.
        Green labels if they will be accepted, red labels if something is wrong.

        Criteria are:
        Volume: float, two decimal points
        Price: float, two decimal points
        Time: hh:mm
        Date: dd.mm.yyyy

        :return:
        """

        vol = self.entry_volume.get()
        price = self.entry_price.get()
        time = self.entry_time.get()
        date = self.entry_date.get()

        global VOL
        global PRICE
        global DATE
        global TIME
        VOL, PRICE, DATE, TIME = False, False, False, False

        # Volume
        try:
            float(vol)
            if len(vol.split(".")) != 2:
                self.label_volume["fg"] = "red"
            else:
                main, decimal = vol.split(".")
                if int(decimal) not in range(100):
                    self.label_volume["fg"] = "red"
                elif len(decimal) != 2:
                    self.label_volume["fg"] = "red"
                else:
                    self.label_volume["fg"] = "green"
                    VOL = True

        except ValueError:
            self.label_volume["fg"] = "red"

        # Price
        try:
            float(price)
            if len(price.split(".")) != 2:
                self.label_price["fg"] = "red"
            else:
                main, decimal = price.split(".")
                if int(decimal) not in range(100):
                    self.label_price["fg"] = "red"
                elif len(decimal) != 2:
                    self.label_price["fg"] = "red"
                else:
                    self.label_price["fg"] = "green"
                    PRICE = True

        except ValueError:
            self.label_price["fg"] = "red"

        # Time
        if len(time.split(":")) != 2:
            self.label_time["fg"] = "red"
        else:
            hh, mm = time.split(":")
            if len(hh) != 2 or len(mm) != 2:
                self.label_time["fg"] = "red"
            else:
                try:
                    if int(hh) not in range(24) or int(mm) not in range(60):
                        self.label_time["fg"] = "red"
                    else:
                        self.label_time["fg"] = "green"
                        TIME = True
                except ValueError:
                    self.label_time["fg"] = "red"

        # Date
        try:
            day, month, year = date.split(".")
            if int(day) not in range(1, 32) or int(month) not in range(1, 13) or int(year) > datetime.date.today().year:
                self.label_date["fg"] = "red"
            else:
                if len(day) != 2 or len(month) != 2 or len(year) != 4:
                    self.label_date["fg"] = "red"
                else:
                    self.label_date["fg"] = "green"
                    DATE = True

        except ValueError:
           self.label_date["fg"] = "red"

        self.after(200, self.sanity_check)


app = Gassy()
app.mainloop()
