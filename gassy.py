import tkinter as tk
import tkinter.messagebox
from tkinter import font
from PIL import Image, ImageTk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import json
import datetime
import time


class Gassy(tk.Tk):
    """
    For embedding matplotlib in tk, see here:
    https://matplotlib.org/3.1.0/gallery/user_interfaces/embedding_in_tk_sgskip.html
    """
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.columnconfigure(0, weight=1)
        self.startup = True
        self.datafile = "/Users/Anders/Documents/github/Gassy/data.json"
        self.backupfile = "/Users/Anders/Documents/github/Gassy/.data_backup.json"

        self.stations = ["Circle K", "Shell", "Best", "Uno-X", "Esso"]
        self.bonuses = ["Trumf", "Coop", "Ingen bonus"]

        self.bonus = tk.StringVar()
        self.bonus.set(self.bonuses[0])
        self.station = tk.StringVar()
        self.station.set(self.stations[0])

        try:
            with open(self.datafile) as f:
                self.data = json.load(f)
        except IOError:
            tk.messagebox.showwarning("Åtvaring", "Fyllingsdata ikkje funne!")

        self.mainwindow = MainWindow(self)
        self.show_main(self)
        self.startup = False

    def show_main(self, windowtoforget):
        self.mainwindow.grid(row=0, column=0)
        if not self.startup:
            windowtoforget.grid_forget()

    def show_addnew(self):
        self.addnew = AddNew(self)
        self.mainwindow.grid_forget()
        self.addnew.grid(row=0, column=0)

    def show_editfills(self):
        self.editfills = EditFills(self)
        self.mainwindow.grid_forget()
        self.editfills.grid(row=0, column=0)


class MainWindow(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self)
        self.parent = parent
        self.grid(row=0, column=0, sticky=tk.NSEW)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        frame_left = tk.Frame(self)
        frame_right = tk.Frame(self)
        frame_left.grid(row=0, column=0)
        frame_right.grid(row=0, column=1)

        image = ImageTk.PhotoImage(Image.open("frontpage_gassy_small.jpg"))
        label = tk.Label(frame_left, image=image)
        label.image = image
        label.grid(row=0, column=0, sticky=tk.E)

        label_title = tk.Label(frame_right, text="Velkommen til Gassy!", bg="orange")
        label_title.grid(row=0, column=0, sticky=tk.EW, padx=20, pady=10)

        button_add_new_fill = tk.Button(frame_right, text="Ny fylling...", command=self.register_new_fill)
        button_add_new_fill.grid(row=1, column=0, sticky=tk.EW, padx=20, pady=5)

        button_edit_fills = tk.Button(frame_right, text="Rediger fyllingar...", command=self.edit_fills)
        button_edit_fills.grid(row=2, column=0, sticky=tk.EW, padx=20, pady=5)

        button_exit = tk.Button(frame_right, text="Lukk", command=self.parent.destroy, fg="red")
        button_exit.grid(row=3, column=0, sticky=tk.EW, padx=20, pady=5)

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

    def edit_fills(self):
        self.parent.show_editfills()


class EditFills(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self)
        self.parent = parent
        self.selected = tk.StringVar()

        self.grid(row=0, column=0, sticky=tk.NSEW)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.frame_left = tk.Frame(self)
        self.frame_right = tk.Frame(self)
        self.frame_left.grid(row=0, column=0, sticky=tk.NSEW)
        self.frame_right.grid(row=0, column=1, sticky=tk.NSEW)

        tk.Label(self.frame_left, text="Fyllingar").grid(row=0, column=0, sticky=tk.EW)
        tk.Label(self.frame_right, text="Fyllingsdata").grid(row=0, column=0, sticky=tk.EW)

        # tk Entries for showing data
        self.entry_volume = tk.Entry(self.frame_right)
        self.entry_price = tk.Entry(self.frame_right)
        self.entry_date = tk.Entry(self.frame_right)
        self.entry_time = tk.Entry(self.frame_right)
        option_bonus = tk.OptionMenu(self.frame_right, self.parent.bonus, *self.parent.bonuses)
        option_station = tk.OptionMenu(self.frame_right, self.parent.station, *self.parent.stations)
        self.label_volume = tk.Label(self.frame_right, text="Volum (L): ")
        self.label_price = tk.Label(self.frame_right, text="Literpris (Kr/L): ")
        self.label_date = tk.Label(self.frame_right, text="Dato (åååå-mm-dd): ")
        self.label_time = tk.Label(self.frame_right, text="Klokkeslett (tt:mm): ")
        label_bonus = tk.Label(self.frame_right, text="Bonusprogram: ")
        label_station = tk.Label(self.frame_right, text="Stasjon: ")

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

        for row in range(6):
            tk.Button(self.frame_right, text="Hjelp", command=lambda index=row: self.edit_help(index+1)).grid(row=row+1, column=2)

        tk.Button(self.frame_right, text="Avbryt", command=lambda: self.parent.show_main(self)).grid(row=7, column = 1, sticky=tk.W)
        tk.Button(self.frame_right, text="Oppdater fylling", command=self.update_fill_entry).grid(row=7, column=0)

        global fills
        fills = [fill["date"] for fill in self.parent.data]
        fills = map(lambda x: x.split("-"), fills)

        fills = [datetime.date(*list(map(int, date))) for date in fills]

        ROW = 1
        for i, fill in enumerate(sorted(fills)):
            label = tk.Label(self.frame_left, text=fill)
            label.grid(row=ROW, column=0)
            label.bind("<Button-1>", lambda event, date=fill, i=i: self.show_fill_data(event, date, i))

            ROW += 1

        self.sanity_check()

    def edit_help(self, index):
        if index == 1:
            msg = """
            Her oppgir du antal liter du fylte.
            
            Talet må vere eit desimaltal, med "punktum" 
            som desimalseparator. Talet må også innehalde 
            to desimalar for å vere gyldig.
            
            Nokre døme:
            Rett: 45.23
            Feil: 45,23
            Feil: 45.2
            Feil: 45.223
            """

            image = ImageTk.PhotoImage(Image.open("help_volum.jpg"))
            return InfoBox(self, msg, image)
        elif index == 2:
            msg = """
            Her oppgir du literprisen for fyllinga di. 
            
            Talet må vere eit desimaltal, med "punktum" 
            som desimalseparator. Talet må også innehalde 
            to desimalar for å vere gyldig.
            
            Nokre døme: 
            Rett: 16.99
            Feil: 16,99
            Feil: 16.9
            Feil: 16.991
            """
            image = ImageTk.PhotoImage(Image.open("help_price.jpg"))
            return InfoBox(self, msg, image)
        elif index == 3:
            msg = """
            Her veljer du datoen for fyllinga.
            Formatet er år-månad-dag. Nokre døme:
            
            Rett: 1986-01-07
            Feil: 07-01-2986
            Feil: 07/1-86
            Feil: 7. januar 1986
            Feil: 1986-1-7
            """
            image = ImageTk.PhotoImage(Image.open("help_date.jpg"))
            return InfoBox(self, msg, image)
        elif index == 4:
            msg = """
            Her set du klokkeslettet for fyllinga. 
            Det skal stå nøyaktig klokkeslett på
            kvitteringa, men du kan også leggje inn
            eit omtrentleg klokkeslett.
            
            Legg inn i 24-timarsformat. Nokre døme:
            
            Rett: 00:01
            Feil: 24:01
            Feil: 23:4
            Feil: 23:411
            """
            image = ImageTk.PhotoImage(Image.open("help_time.jpg"))
            return InfoBox(self, msg, image)
        elif index == 5:
            msg = """
            Her veljer du det bonusprogrammet du brukte.
            Dersom du ikkje brukde noko bonusprogram,
            så veljer du "Ingen bonus".
            
            Hugs at somme bonusprogram ikkje er 
            kompatible med somme stasjonar. Pass
            på at du veljer korrekte kombinasjonar.
            """
            image = ImageTk.PhotoImage(Image.open("help_bonus.jpg"))
            return InfoBox(self, msg, image)
        elif index == 6:
            msg = """
            Her veljer du bensinstasjonen der
            du fylte drivstoff. Dersom kjeden
            ikkje er lagt inn i Gassy, så send
            ein e-post og etterspør kjeden.
            
            anders.brakestad@gmail.com
            """
            image = ImageTk.PhotoImage(Image.open("help_station.jpg"))
            return InfoBox(self, msg, image)


    def show_fill_data(self, event, date, index):
        # First update all labels such that the one clicked is green
        ROW = 1
        for i, fill in enumerate(sorted(fills)):
            if i == index:
                label = tk.Label(self.frame_left, text=fill, bg="lightgreen")
            else:
                label = tk.Label(self.frame_left, text=fill)
            label.grid(row=ROW, column=0)
            label.bind("<Button-1>", lambda event, date=fill, i=i: self.show_fill_data(event, date, i))

            ROW += 1

        self.selected.set(date)
        # Then display the fill data
        entry = self.get_fill_from_date(self.parent.data, date)

        self.entry_volume.delete(0, tk.END)
        self.entry_volume.insert(0, entry["volume"])

        self.entry_price.delete(0, tk.END)
        self.entry_price.insert(0, entry["price"])

        self.entry_date.delete(0, tk.END)
        self.entry_date.insert(0, entry["date"])

        self.entry_time.delete(0, tk.END)
        self.entry_time.insert(0, entry["time"])

        self.parent.bonus.set("Ingen bonus" if entry["bonus"] == "False" else entry["bonus"])
        self.parent.station.set(entry["station"])

    @staticmethod
    def get_fill_from_date(data, query):
        """
        Fetch the fill data dict from fill data by matching with a date.
        Only works if all dates are unique, but this is a reasonable assumption.

        :return: The fill information for the corresponding date
        """
        day = query.day if len(str(query.day)) > 1 else "0" + str(query.day)
        month = query.month if len(str(query.month)) > 1 else "0" + str(query.month)
        for entry in data:
            if entry["date"] == f"{query.year}-{month}-{day}":
                return entry

    def update_fill_entry(self):
        """
        Update the fill entry if it is filled out correctly. Ask for confirmation before
        overwriting data.
        :return:
        """

        if not VOL_EDIT or not PRICE_EDIT or not DATE_EDIT or not TIME_EDIT:
            tk.messagebox.showerror("Feilmelding", "Du har oppgitt verdiar i feil format.")
            return
        elif not tk.messagebox.askyesno("Gassy", "Er du sikker på at du vil endre informasjonen for denne fyllinga?"):
            return

        # First make a dict containing the updated data
        updated_data = {
            "volume": self.entry_volume.get(),
            "price": self.entry_price.get(),
            "time": self.entry_time.get(),
            "date": self.entry_date.get(),
            "bonus": "False" if self.parent.bonus.get() == "Ingen bonus" else self.parent.bonus.get(),
            "station": self.parent.station.get()
        }

        # Now collect all OTHER fill entries from the original data file
        other_data = []
        for entry in self.parent.data:
            if entry["date"] != self.selected.get():
                other_data.append(entry)

        with open(self.parent.backupfile, "w") as backupdata:
            json.dump(self.parent.data, backupdata, indent=4)

        with open(self.parent.datafile, "w") as maindata:
            other_data.append(updated_data)
            json.dump(other_data, maindata, indent=4)

        tk.messagebox.showinfo("Gassy", "Fyllingsdata oppdatert!")

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

        global VOL_EDIT
        global PRICE_EDIT
        global DATE_EDIT
        global TIME_EDIT
        VOL_EDIT, PRICE_EDIT, DATE_EDIT, TIME_EDIT = False, False, False, False

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
                    VOL_EDIT = True

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
                    PRICE_EDIT = True

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
                        TIME_EDIT = True
                except ValueError:
                    self.label_time["fg"] = "red"

        # Date
        try:
            year, month, day = date.split("-")
            if int(day) not in range(1, 32) or int(month) not in range(1, 13) or int(year) > datetime.date.today().year:
                self.label_date["fg"] = "red"
            else:
                if len(day) != 2 or len(month) != 2 or len(year) != 4:
                    self.label_date["fg"] = "red"
                else:
                    self.label_date["fg"] = "green"
                    DATE_EDIT = True

        except ValueError:
           self.label_date["fg"] = "red"

        self.after(200, self.sanity_check)


class AddNew(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self)
        self.parent = parent

        self.grid(row=0, column=0, sticky=tk.NSEW)

        tk.Label(self, text="Legg til ny fylling").grid(row=0, column=0)
        self.entry_volume = tk.Entry(self)
        self.entry_price = tk.Entry(self)
        self.entry_date = tk.Entry(self)
        self.entry_time = tk.Entry(self)
        option_bonus = tk.OptionMenu(self, self.parent.bonus, *self.parent.bonuses)
        option_station = tk.OptionMenu(self, self.parent.station, *self.parent.stations)
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

        for row in range(6):
            tk.Button(self, text="Hjelp", command=lambda index=row: self.edit_help(index+1)).grid(row=row+1, column=2)

        tk.Button(self, text="Lagre", command=self.append_new_fill).grid(row=7, column=0, sticky=tk.W)
        tk.Button(self, text="Avbryt", command=lambda: self.parent.show_main(self)).grid(row=7,
                                                                                         column=0, sticky=tk.E)
        #tk.Button(self, text="Lukk", command=self.parent.destroy).grid(row=9, column=0)

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
        data["volume"] = self.entry_volume.get()
        data["price"] = self.entry_price.get()
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
            year, month, day = date.split("-")
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

    def edit_help(self, index):
        if index == 1:
            msg = """
            Her oppgir du antal liter du fylte.

            Talet må vere eit desimaltal, med "punktum" 
            som desimalseparator. Talet må også innehalde 
            to desimalar for å vere gyldig.

            Nokre døme:
            Rett: 45.23
            Feil: 45,23
            Feil: 45.2
            Feil: 45.223
            """

            image = ImageTk.PhotoImage(Image.open("help_volum.jpg"))
            return InfoBox(self, msg, image)
        elif index == 2:
            msg = """
            Her oppgir du literprisen for fyllinga di. 

            Talet må vere eit desimaltal, med "punktum" 
            som desimalseparator. Talet må også innehalde 
            to desimalar for å vere gyldig.

            Nokre døme: 
            Rett: 16.99
            Feil: 16,99
            Feil: 16.9
            Feil: 16.991
            """
            image = ImageTk.PhotoImage(Image.open("help_price.jpg"))
            return InfoBox(self, msg, image)
        elif index == 3:
            msg = """
            Her veljer du datoen for fyllinga.
            Formatet er år-månad-dag. Nokre døme:

            Rett: 1986-01-07
            Feil: 07-01-2986
            Feil: 07/1-86
            Feil: 7. januar 1986
            Feil: 1986-1-7
            """
            image = ImageTk.PhotoImage(Image.open("help_date.jpg"))
            return InfoBox(self, msg, image)
        elif index == 4:
            msg = """
            Her set du klokkeslettet for fyllinga. 
            Det skal stå nøyaktig klokkeslett på
            kvitteringa, men du kan også leggje inn
            eit omtrentleg klokkeslett.

            Legg inn i 24-timarsformat. Nokre døme:

            Rett: 00:01
            Feil: 24:01
            Feil: 23:4
            Feil: 23:411
            """
            image = ImageTk.PhotoImage(Image.open("help_time.jpg"))
            return InfoBox(self, msg, image)
        elif index == 5:
            msg = """
            Her veljer du det bonusprogrammet du brukte.
            Dersom du ikkje brukde noko bonusprogram,
            så veljer du "Ingen bonus".

            Hugs at somme bonusprogram ikkje er 
            kompatible med somme stasjonar. Pass
            på at du veljer korrekte kombinasjonar.
            """
            image = ImageTk.PhotoImage(Image.open("help_bonus.jpg"))
            return InfoBox(self, msg, image)
        elif index == 6:
            msg = """
            Her veljer du bensinstasjonen der
            du fylte drivstoff. Dersom kjeden
            ikkje er lagt inn i Gassy, så send
            ein e-post og etterspør kjeden.

            anders.brakestad@gmail.com
            """
            image = ImageTk.PhotoImage(Image.open("help_station.jpg"))
            return InfoBox(self, msg, image)


class InfoBox(tk.Toplevel):
    def __init__(self, parent, msg, image):
        tk.Toplevel.__init__(self, parent)
        self.parent = parent
        self.msg = msg
        self.image = image

        self.title = "Gassy"
        self.font = font.Font(family="Optima", size=20)

        frame_left = tk.Frame(self)
        frame_right = tk.Frame(self)
        frame_left.grid(row=0, column=0, sticky=tk.NSEW)
        frame_right.grid(row=0, column=1, sticky=tk.NSEW)

        label_image = tk.Label(frame_left, image=self.image)
        label_image.grid(row=0, column=0, sticky=tk.N)
        label_image.image = self.image

        textbox = tk.Text(frame_right, font=self.font, width=40, height=12)
        textbox.grid(row=0, column=0, sticky=tk.NSEW)
        textbox.insert(tk.END, self.msg)
        textbox.config(state=tk.DISABLED)

        tk.Button(frame_left, text="Den er grei!", font=self.font, command=self.destroy).grid(row=1, column=0)


app = Gassy()
app.resizable(False, False)
app.title("Gassy")
app.mainloop()
