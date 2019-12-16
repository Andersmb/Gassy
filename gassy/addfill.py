from tkinter import messagebox

from mywidgets import *
from helpers import *


class AddFill(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self)
        self.parent = parent
        self.parent.dbug("OPENING ADD NEW FILL", h=True)
        pady = 5
        padx = 5

        self.grid(row=0, column=0, sticky=tk.NSEW)

        MyHeading(self, text="Legg til ny fylling").grid(row=0, column=0)
        self.entry_volume = MyEntry(self)
        self.entry_price = MyEntry(self)
        self.entry_date = MyEntry(self)
        self.entry_time = MyEntry(self)
        self.entry_comment = MyEntry(self)

        self.label_volume = MyLabel(self, text="Volum: ")
        self.label_price = MyLabel(self, text="Literpris: ")
        self.label_date = MyLabel(self, text="Dato (åååå-mm-dd): ")
        self.label_time = MyLabel(self, text="Klokkeslett (tt:mm): ")
        label_bonus = MyLabel(self, text="Bonusprogram: ")
        label_station = MyLabel(self, text="Stasjon: ")
        self.label_comment = MyLabel(self, text="Kommentar")

        self.label_volume.grid(row=1, column=0, sticky=tk.W, padx=padx, pady=pady)
        self.label_price.grid(row=2, column=0, sticky=tk.W, padx=padx, pady=pady)
        self.label_date.grid(row=3, column=0, sticky=tk.W, padx=padx, pady=pady)
        self.label_time.grid(row=4, column=0, sticky=tk.W, padx=padx, pady=pady)
        self.label_comment.grid(row=5, column=0, sticky=tk.W, padx=padx, pady=pady)
        label_bonus.grid(row=6, column=0, sticky=tk.W, padx=padx, pady=pady)
        label_station.grid(row=7, column=0, sticky=tk.W, padx=padx, pady=pady)

        self.entry_volume.grid(row=1, column=1, sticky=tk.W, padx=padx, pady=pady)
        self.entry_price.grid(row=2, column=1, sticky=tk.W, padx=padx, pady=pady)
        self.entry_date.grid(row=3, column=1, sticky=tk.W, padx=padx, pady=pady)
        self.entry_time.grid(row=4, column=1, sticky=tk.W, padx=padx, pady=pady)
        self.entry_comment.grid(row=5, column=1, sticky=tk.W, padx=padx, pady=pady)

        MyOptionMenu(self, self.parent.bonus, *self.parent.bonuses).grid(row=6, column=1, sticky=tk.W, padx=padx, pady=pady)
        MyOptionMenu(self, self.parent.station, *self.parent.stations).grid(row=7, column=1, sticky=tk.W, padx=padx, pady=pady)

        # Put focus on volume entry
        self.entry_volume.focus_set()

        for row in range(7):
            MyButton(self,
                     text="Hjelp",
                     command=lambda index=row: edit_help(self.parent, index + 1, self.parent.rootdir)).grid(row=row + 1,
                                                                                               column=2,
                                                                                               padx=padx, pady=pady)

        MyButton(self, text="Legg til fylling", command=self.append_new_fill).grid(row=8, column=0, sticky=tk.W, padx=padx,
                                                                        pady=pady)
        MyButton(self, text="Attende", command=lambda: self.parent.show_main(self)).grid(row=9, column=0, sticky=tk.W,
                                                                                         padx=padx, pady=pady)

        self.sanity_check()

    def append_new_fill(self):
        """
        Update the data file by appending the newly filled in information, if the information
        is in the correct format. If not, then show error message.
        :return: None
        """
        if not VOL or not PRICE or not DATE or not TIME:
            tk.messagebox.showerror("Feilmelding", "Du har oppgitt verdiar i feil format.")
            return
        elif not tk.messagebox.askyesno("Åtvaring", "Er du sikker på at du vil leggje til ny fylling?"):
            return

        data = {}
        data["bonus"] = "False" if self.parent.bonus.get() == "Ingen bonus" else self.parent.bonus.get()
        data["station"] = self.parent.station.get()
        data["volume"] = float(self.entry_volume.get())
        data["price"] = float(self.entry_price.get())
        data["time"] = self.entry_time.get()
        data["date"] = self.entry_date.get()
        data["comment"] = self.entry_comment.get()

        with open(self.parent.f_data, "w") as f:
            self.parent.data.append(data)
            json.dump(self.parent.data, f, indent=4)

        self.parent.dbug("New fill added to datafile.")
        tk.messagebox.showinfo(self.parent.name, "Ny fylling lagt til!")

    def sanity_check(self):
        """
        Evaluate whether the information provided in Entries are valid.
        Continuously monitor whether the criteria are fulfilled.
        Green labels if they will be accepted, red labels if something is wrong.

        Criteria are:
        Volume: float, two decimal points
        Price: float, two decimal points
        Time: hh:mm
        Date: yyyy-mm-dd

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