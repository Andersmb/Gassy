from tkinter import messagebox
import datetime
from mywidgets import *
from helpers import *


class EditFills(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self)
        self.parent = parent
        self.parent.dbug("OPENING EDIT FILLS", h=True)

        self.selected = tk.StringVar()

        self.grid(row=0, column=0, sticky=tk.NSEW)

        # Frame for left side title
        self.frame_left_title = tk.Frame(self)
        self.frame_left_title.grid(row=0, column=0, sticky=tk.NW)

        # Frame to contain canvas and scroll
        self.frame_left_main = tk.Frame(self)
        self.frame_left_main.grid(row=1, column=0, sticky=tk.NW)

        # Frame to contain fill data
        self.frame_right = tk.Frame(self)
        self.frame_right.grid(row=0, column=2, rowspan=2, sticky=tk.NSEW)

        # Add canvas to hold dates
        self.canvas = tk.Canvas(self.frame_left_main)
        self.canvas.grid(row=0, column=0)

        # Make vertical scrollbar
        self.vsb = tk.Scrollbar(self.frame_left_main, command=self.canvas.yview)
        self.vsb.grid(row=0, column=0, sticky=tk.NS)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        # Add frame to canvas to hold dates
        self.frame_dates = tk.Frame(self.canvas)

        # Create canvas window to hold the date frame
        self.canvas.create_window((0, 0), window=self.frame_dates, anchor=tk.NW)

        self.frame_dates.bind("<Configure>", self.update_scrollregion)

        # Make title labels
        MyHeading(self.frame_left_title, text="Fyllingar").grid(row=0, column=0, sticky=tk.W)
        MyHeading(self.frame_right, text="Fyllingsdata").grid(row=0, column=0, columnspan=3, sticky=tk.W)

        # tk Entries for showing data
        self.entry_volume = MyEntry(self.frame_right, width=20)
        self.entry_price = MyEntry(self.frame_right, width=20)
        self.entry_date = MyEntry(self.frame_right, width=20)
        self.entry_time = MyEntry(self.frame_right, width=20)
        self.entry_comment = MyEntry(self.frame_right, width=20)
        MyOptionMenu(self.frame_right, self.parent.bonus, *self.parent.bonuses).grid(row=6, column=1, sticky=tk.W)
        MyOptionMenu(self.frame_right, self.parent.station, *self.parent.stations).grid(row=7, column=1, sticky=tk.W)
        self.label_volume = MyLabel(self.frame_right, text="Volum (L): ")
        self.label_price = MyLabel(self.frame_right, text="Literpris (Kr/L): ")
        self.label_date = MyLabel(self.frame_right, text="Dato (åååå-mm-dd): ")
        self.label_time = MyLabel(self.frame_right, text="Klokkeslett (tt:mm): ")
        self.label_comment = MyLabel(self.frame_right, text="Kommentar: ")

        MyLabel(self.frame_right, text="Bonusprogram: ").grid(row=6, column=0, sticky=tk.W, pady=5, padx=5)
        MyLabel(self.frame_right, text="Stasjon: ").grid(row=7, column=0, sticky=tk.W, pady=5, padx=5)

        self.label_volume.grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        self.label_price.grid(row=2, column=0, sticky=tk.W, pady=5, padx=5)
        self.label_date.grid(row=3, column=0, sticky=tk.W, pady=5, padx=5)
        self.label_time.grid(row=4, column=0, sticky=tk.W, pady=5, padx=5)
        self.label_comment.grid(row=5, column=0, sticky=tk.W, pady=5, padx=5)
        self.entry_volume.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        self.entry_price.grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
        self.entry_date.grid(row=3, column=1, sticky=tk.W, pady=5, padx=5)
        self.entry_time.grid(row=4, column=1, sticky=tk.W, pady=5, padx=5)
        self.entry_comment.grid(row=5, column=1, sticky=tk.W, pady=5, padx=5)

        # Put focus on volume entry
        self.entry_volume.focus_set()

        for row in range(7):
            MyButton(self.frame_right,
                     text="Hjelp",
                     command=lambda index=row: edit_help(self.parent, index + 1,
                                                         self.parent.rootdir)).grid(row=row + 1, column=2, pady=5,
                                                                                    padx=5, sticky=tk.W)

        MyButton(self.frame_right, text="Attende", command=self.close).grid(row=8, column=1, sticky=tk.W, pady=5, padx=5)
        MyButton(self.frame_right,
                 text="Oppdater fylling",
                 command=self.update_fill_entry).grid(row=8, column=0, pady=5, padx=5, sticky=tk.W)

        global fills
        fills = [fill["date"] for fill in self.parent.data]
        fills = map(lambda x: x.split("-"), fills)

        fills = [datetime.date(*list(map(int, date))) for date in fills]

        ROW = 1
        for i, fill in enumerate(sorted(fills, reverse=True)):
            label = MyLabel(self.frame_dates, text=fill, height=1)
            label.grid(row=ROW, column=0)
            label.bind("<Button-1>", lambda event, date=fill, i=i: self.show_fill_data(event, date, i))

            ROW += 1

        self.sanity_check()

    def close(self):
        self.parent.show_main(self)
        self.destroy()

    def update_scrollregion(self, event):
        """Update scroll region of frame holding dates when new dates are added"""
        self.canvas.configure(scrollregion=self.canvas.bbox(tk.ALL))

    def show_fill_data(self, event, date, index):
        """
        Update all date labels, and color the one clicked to green.

        First re-grid all labels. The one that was clicked will become green.
        Then get the fill data based on the date clicked, and insert this into the
        widgets.
        :param event: bind event from clicking on a label
        :param date: date that is clicked
        :param index: index of placement for date labels
        :return: None
        """
        # First update all labels such that the one clicked is green
        ROW = 1
        for i, fill in enumerate(sorted(fills, reverse=True)):
            if i == index:
                label = MyLabel(self.frame_dates, text=fill, bg="lightgreen", height=1)
            else:
                label = MyLabel(self.frame_dates, text=fill, height=1)
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

        self.entry_comment.delete(0, tk.END)
        self.entry_comment.insert(0, entry["comment"])

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
        :return: None
        """

        if not VOL_EDIT or not PRICE_EDIT or not DATE_EDIT or not TIME_EDIT:
            tk.messagebox.showerror("Feilmelding", "Du har oppgitt verdiar i feil format.")
            return
        elif not tk.messagebox.askyesno("Gassy", "Er du sikker på at du vil endre informasjonen for denne fyllinga?"):
            return

        # First make a dict containing the updated data
        updated_data = {
            "volume": float(self.entry_volume.get()),
            "price": float(self.entry_price.get()),
            "time": self.entry_time.get(),
            "date": self.entry_date.get(),
            "bonus": "False" if self.parent.bonus.get() == "Ingen bonus" else self.parent.bonus.get(),
            "station": self.parent.station.get(),
            "comment": self.entry_comment.get()
        }

        # Now collect all OTHER fill entries from the original data file
        other_data = []
        for entry in self.parent.data:
            if entry["date"] != self.selected.get():
                other_data.append(entry)

        with open(self.parent.f_data, "w") as f:
            other_data.append(updated_data)
            json.dump(other_data, f, indent=4)
            self.parent.dbug(f"Fill from {self.selected.get()} updated.")

        self.parent.data = self.parent.load_data()
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
        Date: yyyy-mm-dd

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