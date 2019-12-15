import tkinter as tk
from tkinter import messagebox, font
from PIL import Image, ImageTk
from collections import OrderedDict
import matplotlib

matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import os
import json
import datetime
from copy import deepcopy
import smtplib

DEV = True
verbose = True


class Gassy(tk.Tk):
    def __init__(self, *args, **kwargs):
        self.dbug("STARTING GASSY", h=True)
        tk.Tk.__init__(self, *args, **kwargs)
        self.columnconfigure(0, weight=1)
        self.startup = True
        self.name = "Gassy-DEV" if DEV else "Gassy"
        self.title(self.name)

        # Set working directory and key dirs and files
        self.rootdir = os.path.dirname(os.path.abspath(__file__))
        self.d_project = os.path.join(os.path.expanduser("~"), self.name)
        self.d_backups = os.path.join(self.d_project, "Sikkerheitskopiar")
        self.f_settings = os.path.join(self.d_project, "Innstillingar.json")
        self.f_data = os.path.join(self.d_project, "Fyllingsdata.json")

        # Initialize variables
        self.bonus = tk.StringVar()
        self.station = tk.StringVar()
        self.automatic_backup = tk.BooleanVar()

        # Define the gas station options and bonus options
        self.stations = ["Circle K", "Shell", "Best", "Uno-X", "Esso", "OKQ8", "Ukjend"]
        self.bonuses = ["Trumf", "Coop", "Ingen bonus", "Ukjend"]

        # Set default values for station and bonus
        self.bonus.set(self.bonuses[0])
        self.station.set(self.stations[0])

        # Define fonts
        self.font_heading = font.Font(family="Optima", size=20)
        self.font_main = font.Font(family="Optima", size=14)

        # Define default user settings
        self.defaults = {
            "automatic_backup": False
        }

        # Load settings
        self.current_settings = self.load_settings()
        self.set_system_variables()

        # Load data
        self.data = self.load_data()

        # Initialize the main window
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

    def show_feedback(self):
        self.feedback = Feedback(self)
        self.mainwindow.grid_forget()
        self.feedback.grid(row=0, column=0)

    def show_graphing(self):
        if len(self.data) == 0:
            msg = """Du har ikkje registrert fyllingar endå, så denne funksjonaliteten vil ikkje fungere skikkeleg."""
            messagebox.showwarning(self.name, msg)
        self.graphing = Graphing(self)
        self.mainwindow.grid_forget()
        self.graphing.grid(row=0, column=0)

    def show_settings(self):
        self.settings = Settings(self)
        self.mainwindow.grid_forget()
        self.settings.grid(row=0, column=0)

    def load_data(self):
        """
        Attempt to open data file.

        If file does not exist, then create empty file and return empty list.

        json.decoder.JSONDecodeError is most likely raised if the data file is empty.
        We just catch this and return an empty list.
        :return: data list
        """
        self.dbug("LOADING DATA", h=True)
        try:
            self.dbug(f"Attempting to load {self.f_data}")
            with open(self.f_data) as f:
                d = json.load(f)
                self.dbug(f"...successfully loaded datafile with {len(d)} fills.")
                return d
        except IOError:
            self.dbug("...data file not found.")
            open(self.f_data, "a").close()
            self.dbug("...new data file created.")
            return []
        except json.decoder.JSONDecodeError:
            self.dbug("...found empty data file.")
            return []

    def load_settings(self):
        """
        Attempt to load the settings file from default path, and assign settings to variable.
        If no file is found, assign defaults to variable and create empty file.
        :return:
        """
        self.dbug("LOADING SETTINGS", h=True)
        self.dbug(f"Checking if default project dir exists... ({self.d_project})")
        if not os.path.isdir(self.d_project):
            self.dbug("...it does not exist.")
            os.makedirs(self.d_project)
            self.dbug("...created default project dir.")
        else:
            self.dbug("... it exists.")

        try:
            self.dbug("Attempting to read settings file...")
            with open(self.f_settings) as f:
                settings = json.load(f)
                self.dbug("...successfully read settings.")
                return settings

        except IOError:
            self.dbug("...settings file not found. Using defaults.")
            open(self.f_settings, "w").close()
            self.dbug(f"...created settings file: {self.f_settings}")
            return deepcopy(self.defaults)

        except json.decoder.JSONDecodeError:
            self.dbug("...error de-serializing JSON. Using defaults")
            return deepcopy(self.defaults)

    def set_system_variables(self):
        """
        Set user variables to the current settings
        :return:
        """
        self.dbug("SETTING SYSTEM VARIABLES", h=True)

        self.automatic_backup.set(self.current_settings["automatic_backup"])
        self.dbug(f"Automatic backup: {self.automatic_backup.get()}")

    def dump_settings(self):
        self.dbug(f"DUMPING SETTINGS TO {self.f_settings}", h=True)
        try:
            with open(self.f_settings, "w") as f:
                json.dump(self.current_settings, f, indent=4)
        except FileNotFoundError:
            if not os.path.isdir(self.d_project):
                msg = f"{self.name} si prosjektmappe ({self.d_project})finns ikkje. Vil du opprette ho?"
                if tk.messagebox.askyesno(self.name, msg):
                    os.makedirs(self.d_project)
            else:
                tk.messagebox.showerror(self.name, "Ukjend feil, venlegst rapporter i detalj korleis denne meldinga oppstod.")

    def dbug(self, s, h=False):
        if h and verbose:
            print(f"[{current_time()}] ---------------------------------------")
        if s is not None and verbose:
            print(f"[{current_time()}] {s}")

    def backup(self):
        """Copy data file to the backup location"""
        self.dbug("PREPARING BACKUP...", h=True)
        filename = os.path.join(self.d_backups, f"sikkerheitskopi_{current_date()}_{len(self.data)}fyllingar.json")

        if os.path.isdir(self.d_backups):
            with open(filename, "w") as f:
                json.dump(self.data, f, indent=4)
                self.dbug("...data backed up.")
        else:
            self.dbug(f"...directory for storing backups does not exist.")
            msg = f"""Mappa der du vil lagre sikkerheitskopiane eksisterer ikkje. Vil du opprette ho? \n({
            self.d_backups})"""
            if messagebox.askyesno(self.name, msg):
                os.makedirs(self.d_backups)
                self.dbug(f"...backup dir created: {self.d_backups}")
                with open(filename, "w") as f:
                    json.dump(self.data, f, indent=4)
                    self.dbug("...data backed up")


class MainWindow(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self)
        self.parent = parent
        self.parent.dbug("OPENING MAIN WINDOW", h=True)
        self.grid(row=0, column=0, sticky=tk.NSEW)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.frame_left = tk.Frame(self)
        frame_right = tk.Frame(self)
        self.frame_left.grid(row=0, column=0)
        frame_right.grid(row=0, column=1)

        image = ImageTk.PhotoImage(Image.open(os.path.join(self.parent.rootdir, "Bilete", "frontpage_gassy_small.jpg")))
        label = tk.Label(self.frame_left, image=image)
        label.image = image
        label.grid(row=0, column=0, sticky=tk.E)

        tk.Label(frame_right,
                 text="Velkommen til Gassy!",
                 bg="orange",
                 font=self.parent.font_heading).grid(row=0, column=0, sticky=tk.EW, padx=20, pady=10)

        tk.Button(frame_right,
                  text="Ny fylling...",
                  command=self.parent.show_addnew,
                  font=self.parent.font_main).grid(row=1, column=0, sticky=tk.EW, padx=20, pady=5)

        tk.Button(frame_right,
                  text="Rediger fyllingar...",
                  command=self.parent.show_editfills,
                  font=self.parent.font_main).grid(row=2, column=0, sticky=tk.EW, padx=20, pady=5)

        tk.Button(frame_right,
                  text="Analysar...",
                  command=self.parent.show_graphing,
                  font=self.parent.font_main).grid(row=3, column=0, sticky=tk.EW, padx=20, pady=5)

        tk.Button(frame_right,
                  text="Oppdater fyllingsdata",
                  command=self.refresh_data,
                  font=self.parent.font_main).grid(row=4, column=0, sticky=tk.EW, padx=20, pady=5)

        tk.Button(frame_right,
                  text="Innstillingar",
                  command=self.parent.show_settings,
                  font=self.parent.font_main).grid(row=5, column=0, sticky=tk.EW, padx=20, pady=5)

        tk.Button(frame_right,
                  text="Ris og ros",
                  command=self.parent.show_feedback,
                  font=self.parent.font_main).grid(row=6, column=0, sticky=tk.EW, padx=20, pady=5)

        tk.Button(frame_right,
                  text="Avslutt",
                  command=self.parent.destroy,
                  fg="red", font=self.parent.font_main).grid(row=7, column=0, sticky=tk.EW, padx=20, pady=5)

        if len(self.parent.data) == 0:
            tk.Label(self.frame_left, text="Datafila di er tom :(",
                     font=self.parent.font_main, fg="red").grid(row=1, column=0)
        else:
            if len(self.parent.data) > 1:
                tk.Label(self.frame_left, text=f"Datafila di har {len(self.parent.data)} fyllingar :)",
                         font=self.parent.font_main, fg="green").grid(row=1, column=0)
            else:
                tk.Label(self.frame_left, text=f"Datafila di har {len(self.parent.data)} fylling :)",
                         font=self.parent.font_main, fg="green").grid(row=1, column=0)

    def refresh_data(self):
        self.parent.data = self.parent.load_data()
        image = ImageTk.PhotoImage(Image.open(os.path.join(self.parent.rootdir, "Bilete", "frontpage_gassy_small_green.jpg")))
        label = tk.Label(self.frame_left, image=image)
        label.image = image
        label.grid(row=0, column=0, sticky=tk.E)
        self.after(500, lambda: self.__init__(self.parent))


class Feedback(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self)
        self.parent = parent
        self.parent.dbug("OPENING FEEDBACK", h=True)
        self.grid(row=0, column=0, sticky=tk.NSEW)

        self.mail = "gassy.feedback@gmail.com"
        self.pwd = "Sd!geZnIIWPQQ4BrhkLY"

        # Define subject categories
        placeholder = "Vel emne              "
        self.subject_options = ["Ny funksjon           ",
                                "Feil i koden          ",
                                "Ros                   ",
                                "Anna                  "]
        self.subject = tk.StringVar()
        self.subject.set(placeholder)  # Default is a placeholder

        # Title
        tk.Label(self,
                 text="Gi tilbakemelding",
                 font=self.parent.font_heading,
                 bg="orange").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)

        # Choose subject
        tk.OptionMenu(self, self.subject, *self.subject_options).grid(row=1, sticky=tk.W, padx=10, pady=5)

        # Main body
        tk.Label(self, text="Skriv di tilbakemelding her").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)

        self.body = tk.Text(self, font=self.parent.font_main, relief=tk.GROOVE)
        self.body.grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        self.body.focus_set()

        tk.Button(self,
                  text="Send tilbakemelding",
                  font=self.parent.font_main,
                  command=self.send_feedback).grid(row=4, column=0, sticky=tk.W, padx=10, pady=5)
        tk.Button(self,
                  text="Attende",
                  font=self.parent.font_main,
                  command=lambda: self.parent.show_main(self)).grid(row=5, column=0, sticky=tk.W, padx=10, pady=5)

    def send_feedback(self):
        # Set up connection
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()

        # encrypt
        server.starttls()

        # Log in
        server.login(self.mail, self.pwd)

        msg = f"""Subject: {self.subject.get().strip()}\n\n{self.body.get("1.0", tk.END)}"""

        if not self.body.get("1.0", tk.END).strip() == "":
            server.sendmail(self.mail, self.mail, msg)
            tk.messagebox.showinfo(self.parent.name, "Tusen takk for tilbakemeldinga! :)")
        else:
            tk.messagebox.showwarning(self.parent.name, "Du har ikkje skrive noko i tekstboksen.")


class Settings(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self)
        self.parent = parent
        self.parent.dbug("OPENING SETTINGS", h=True)

        self.grid(row=0, column=0, sticky=tk.NSEW)

        self.frame = tk.Frame(self)
        self.frame.grid(row=0, column=0)

        # Labels
        tk.Label(self.frame, text="Innstillingar", font=self.parent.font_heading,
                 bg="orange").grid(row=0, column=0, sticky=tk.W)

        tk.Label(self.frame, text=f"Prosjektmappe for {self.parent.name}:",
                 font=self.parent.font_main).grid(row=1, column=0, sticky=tk.W)
        tk.Label(self.frame, text=self.parent.d_project,
                 font=self.parent.font_main).grid(row=1, column=1, sticky=tk.W)

        tk.Label(self.frame, text="Datafil:", font=self.parent.font_main).grid(row=2, column=0, sticky=tk.W)
        tk.Label(self.frame, text=self.parent.f_data,
                 font=self.parent.font_main).grid(row=2, column=1, sticky=tk.W)

        tk.Label(self.frame, text="Innstillingsfil:", font=self.parent.font_main).grid(row=3, column=0, sticky=tk.W)
        tk.Label(self.frame, text=self.parent.f_settings,
                 font=self.parent.font_main).grid(row=3, column=1, sticky=tk.W)

        tk.Label(self.frame,
                 text="Mappe for sikkerheitskopiar:",
                 font=self.parent.font_main).grid(row=4, column=0, sticky=tk.W)
        tk.Label(self.frame,
                 text=self.parent.d_backups,
                 font=self.parent.font_main).grid(row=4, column=1, sticky=tk.W)

        # Check buttons
        tk.Checkbutton(self.frame, text=f"Automatisk sikkerheitskopi når du avsluttar {self.parent.name}?",
                       variable=self.parent.automatic_backup).grid(row=5, column=0, sticky=tk.W)

        # Buttons
        tk.Button(self.frame, text="Ta sikkerheitskopi",
                  command=self.parent.backup,
                  font=self.parent.font_main).grid(row=6, column=0, sticky=tk.W)
        tk.Button(self.frame, text="Lagre innstillingar",
                  command=self.get_new_settings,
                  font=self.parent.font_main).grid(row=7, column=0, sticky=tk.W)
        tk.Button(self.frame, text="Attende",
                  command=lambda: self.parent.show_main(self),
                  font=self.parent.font_main).grid(row=8, column=0, sticky=tk.W)

    def get_new_settings(self):
        self.parent.current_settings["automatic_backup"] = self.parent.automatic_backup.get()

        self.parent.set_system_variables()
        self.parent.dump_settings()

        tk.messagebox.showinfo(self.parent.name, f"Innstillingar lagra i {self.parent.f_settings}")


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
        tk.Label(self.frame_left_title, text="Fyllingar",
                 font=self.parent.font_heading).grid(row=0, column=0, sticky=tk.W)
        tk.Label(self.frame_right, text="Fyllingsdata",
                 font=self.parent.font_heading).grid(row=0, column=0, columnspan=3)

        # tk Entries for showing data
        self.entry_volume = tk.Entry(self.frame_right, font=self.parent.font_main, width=20)
        self.entry_price = tk.Entry(self.frame_right, font=self.parent.font_main, width=20)
        self.entry_date = tk.Entry(self.frame_right, font=self.parent.font_main, width=20)
        self.entry_time = tk.Entry(self.frame_right, font=self.parent.font_main, width=20)
        self.entry_comment = tk.Entry(self.frame_right, font=self.parent.font_main, width=20)
        option_bonus = tk.OptionMenu(self.frame_right, self.parent.bonus, *self.parent.bonuses)
        option_bonus.config(font=self.parent.font_main)
        option_bonus["menu"].config(font=self.parent.font_main)
        option_station = tk.OptionMenu(self.frame_right, self.parent.station, *self.parent.stations)
        option_station.config(font=self.parent.font_main)
        option_station["menu"].config(font=self.parent.font_main)
        self.label_volume = tk.Label(self.frame_right, text="Volum (L): ", font=self.parent.font_main)
        self.label_price = tk.Label(self.frame_right, text="Literpris (Kr/L): ", font=self.parent.font_main)
        self.label_date = tk.Label(self.frame_right, text="Dato (åååå-mm-dd): ", font=self.parent.font_main)
        self.label_time = tk.Label(self.frame_right, text="Klokkeslett (tt:mm): ", font=self.parent.font_main)
        self.label_comment = tk.Label(self.frame_right, text="Kommentar: ", font=self.parent.font_main)
        label_bonus = tk.Label(self.frame_right, text="Bonusprogram: ", font=self.parent.font_main)
        label_station = tk.Label(self.frame_right, text="Stasjon: ", font=self.parent.font_main)

        self.label_volume.grid(row=1, column=0, sticky=tk.E, pady=5, padx=5)
        self.label_price.grid(row=2, column=0, sticky=tk.E, pady=5, padx=5)
        self.label_date.grid(row=3, column=0, sticky=tk.E, pady=5, padx=5)
        self.label_time.grid(row=4, column=0, sticky=tk.E, pady=5, padx=5)
        self.label_comment.grid(row=5, column=0, sticky=tk.E, pady=5, padx=5)
        label_bonus.grid(row=6, column=0, sticky=tk.E, pady=5, padx=5)
        label_station.grid(row=7, column=0, sticky=tk.E, pady=5, padx=5)
        self.entry_volume.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        self.entry_price.grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
        self.entry_date.grid(row=3, column=1, sticky=tk.W, pady=5, padx=5)
        self.entry_time.grid(row=4, column=1, sticky=tk.W, pady=5, padx=5)
        self.entry_comment.grid(row=5, column=1, sticky=tk.W, pady=5, padx=5)
        option_bonus.grid(row=6, column=1, sticky=tk.W, pady=5, padx=5)
        option_station.grid(row=7, column=1, sticky=tk.W, pady=5, padx=5)

        for row in range(7):
            tk.Button(self.frame_right, text="Hjelp",
                      command=lambda index=row: edit_help(index + 1, self.parent.rootdir),
                      font=self.parent.font_main).grid(row=row + 1, column=2, pady=5, padx=5)

        tk.Button(self.frame_right, text="Attende",
                  command=self.close,
                  font=self.parent.font_main).grid(row=8, column=1, sticky=tk.W, pady=5, padx=5)
        tk.Button(self.frame_right, text="Oppdater fylling",
                  command=self.update_fill_entry,
                  font=self.parent.font_main).grid(row=8, column=0, pady=5, padx=5)

        global fills
        fills = [fill["date"] for fill in self.parent.data]
        fills = map(lambda x: x.split("-"), fills)

        fills = [datetime.date(*list(map(int, date))) for date in fills]

        ROW = 1
        for i, fill in enumerate(sorted(fills, reverse=True)):
            label = tk.Label(self.frame_dates, text=fill, font=self.parent.font_main, height=1)
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
                label = tk.Label(self.frame_dates, text=fill, bg="lightgreen", font=self.parent.font_main, height=1)
            else:
                label = tk.Label(self.frame_dates, text=fill, font=self.parent.font_main, height=1)
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


class AddNew(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self)
        self.parent = parent
        self.parent.dbug("OPENING ADD NEW FILL", h=True)

        self.grid(row=0, column=0, sticky=tk.NSEW)

        tk.Label(self, text="Legg til ny fylling", font=self.parent.font_heading,
                 bg="orange").grid(row=0, column=0)
        self.entry_volume = tk.Entry(self, font=self.parent.font_main)
        self.entry_price = tk.Entry(self, font=self.parent.font_main)
        self.entry_date = tk.Entry(self, font=self.parent.font_main)
        self.entry_time = tk.Entry(self, font=self.parent.font_main)
        self.entry_comment = tk.Entry(self, font=self.parent.font_main)

        option_bonus = tk.OptionMenu(self, self.parent.bonus, *self.parent.bonuses)
        option_bonus.config(font=self.parent.font_main)
        option_bonus["menu"].config(font=self.parent.font_main)
        option_station = tk.OptionMenu(self, self.parent.station, *self.parent.stations)
        option_station.config(font=self.parent.font_main)
        option_station["menu"].config(font=self.parent.font_main)
        self.label_volume = tk.Label(self, text="Volum: ", font=self.parent.font_main)
        self.label_price = tk.Label(self, text="Literpris: ", font=self.parent.font_main)
        self.label_date = tk.Label(self, text="Dato (åååå-mm-dd): ", font=self.parent.font_main)
        self.label_time = tk.Label(self, text="Klokkeslett (tt:mm): ", font=self.parent.font_main)
        label_bonus = tk.Label(self, text="Bonusprogram: ", font=self.parent.font_main)
        label_station = tk.Label(self, text="Stasjon: ", font=self.parent.font_main)
        self.label_comment = tk.Label(self, text="Kommentar", font=self.parent.font_main)

        self.label_volume.grid(row=1, column=0, sticky=tk.E)
        self.label_price.grid(row=2, column=0, sticky=tk.E)
        self.label_date.grid(row=3, column=0, sticky=tk.E)
        self.label_time.grid(row=4, column=0, sticky=tk.E)
        self.label_comment.grid(row=5, column=0, sticky=tk.E)
        label_bonus.grid(row=6, column=0, sticky=tk.E)
        label_station.grid(row=7, column=0, sticky=tk.E)

        self.entry_volume.grid(row=1, column=1, sticky=tk.W)
        self.entry_price.grid(row=2, column=1, sticky=tk.W)
        self.entry_date.grid(row=3, column=1, sticky=tk.W)
        self.entry_time.grid(row=4, column=1, sticky=tk.W)
        self.entry_comment.grid(row=5, column=1, sticky=tk.W)
        option_bonus.grid(row=6, column=1, sticky=tk.W)
        option_station.grid(row=7, column=1, sticky=tk.W)

        for row in range(7):
            tk.Button(self, text="Hjelp", command=lambda index=row: edit_help(index + 1, self.parent.rootdir),
                      font=self.parent.font_main).grid(row=row + 1, column=2)

        tk.Button(self, text="Lagre", command=self.append_new_fill,
                  font=self.parent.font_main).grid(row=8, column=0, sticky=tk.W)
        tk.Button(self, text="Attende", command=lambda: self.parent.show_main(self),
                  font=self.parent.font_main).grid(row=8, column=0, sticky=tk.E)

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


class InfoBox(tk.Toplevel):
    def __init__(self, msg, image):
        """
        Custom pop-up window for displaying information, similar to tk.messagebox.showinfo,
        used for displaying help messages.

        :param msg: string containing the info message to be shown in the InfoBox
        :param image: PhotoImage object used to decorate left side of InfoBox
        """
        tk.Toplevel.__init__(self)
        self.msg = msg
        self.image = image
        app.dbug("OPENING INFO BOX", h=True)

        self.title = app.name

        frame_left = tk.Frame(self)
        frame_right = tk.Frame(self)
        frame_left.grid(row=0, column=0, sticky=tk.NSEW)
        frame_right.grid(row=0, column=1, sticky=tk.NSEW)

        label_image = tk.Label(frame_left, image=self.image)
        label_image.grid(row=0, column=0, sticky=tk.N)
        label_image.image = self.image

        textbox = tk.Text(frame_right, width=40, height=12, font=app.font_main)
        textbox.grid(row=0, column=0, sticky=tk.NSEW)
        textbox.insert(tk.END, self.msg)
        textbox.config(state=tk.DISABLED)

        tk.Button(frame_left, text="Den er grei!", font=app.font_main, command=self.destroy).grid(row=1, column=0)


class Graphing(tk.Frame):
    def __init__(self, parent):
        """
        Window for performing plotting analyses of fill data.

        For embedding matplotlib in tk, see here:
        https://matplotlib.org/3.1.0/gallery/user_interfaces/embedding_in_tk_sgskip.html

        :param parent: parent widget
        """
        tk.Frame.__init__(self)
        self.parent = parent
        self.parent.dbug("OPENING ANALYSES", h=True)

        self.grid(row=0, column=0)

        frame_left = tk.Frame(self)
        frame_right = tk.Frame(self)
        frame_left.grid(row=0, column=0)
        frame_right.grid(row=0, column=1)

        image = ImageTk.PhotoImage(Image.open(os.path.join(self.parent.rootdir, "Bilete", "graphing.jpg")))
        label_image = tk.Label(frame_left, image=image)
        label_image.image = image
        label_image.grid(row=0, column=0)

        tk.Label(frame_right, text="Analyse av fyllingsdata", font=self.parent.font_heading,
                 bg="orange").grid(row=0, column=0, sticky=tk.N)

        tk.Button(frame_right, text="Attende",
                  command=lambda: self.parent.show_main(self),
                  font=self.parent.font_main).grid(row=1, column=0, pady=5, padx=5, sticky=tk.W)
        tk.Button(frame_right, text="Korleis har literprisen variert?",
                  command=self.plot_price,
                  font=self.parent.font_main).grid(row=2, column=0, pady=5, padx=5, sticky=tk.W)
        tk.Button(frame_right, text="Kvar har eg fylt drivstoff oftast?",
                  command=self.plot_station_frequency,
                  font=self.parent.font_main).grid(row=3, column=0, pady=5, padx=5, sticky=tk.W)
        tk.Button(frame_right, text="På kva dag fyller eg oftast?",
                  command=self.plot_day_frequency,
                  font=self.parent.font_main).grid(row=4, column=0, pady=5, padx=5, sticky=tk.W)
        tk.Button(frame_right, text="Samandrag",
                  command=self.fill_report,
                  font=self.parent.font_main).grid(row=5, column=0, pady=5, padx=5, sticky=tk.W)

        tk.Button(frame_right, text="Literpris for ulike dagar",
                  command=self.plot_day_price_variation,
                  font=self.parent.font_main).grid(row=6, column=0, pady=5, padx=5, sticky=tk.W)

    def plot_price(self):
        """
        Make scatter plot of the price vs date. Also add dashed line indicating the average price.
        :return: None
        """
        container = tk.Toplevel(self)
        container.resizable(False, False)

        fig = Figure()
        ax = fig.add_subplot(111)

        # Make informative title
        msg = """Her er alle registrerte literprisar lagt inn i eit koordinatsystem, 
        og du kan sjå korleis literprisen har variert. Hold musepeikaren over 
        datapunktene for å vise datoen for fyllinga."""
        tk.Label(container, text=msg).grid(row=0, column=0)
        tk.Button(container, text="Attende", command=container.destroy, font=self.parent.font_main).grid(row=1,
                                                                                                         column=0)

        # Make dummy annotation
        annot = ax.annotate("",
                            xy=(10, 15),
                            xytext=(20, 0),
                            textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="skyblue"),
                            arrowprops=dict(arrowstyle="->"))
        # print(ax.get_xlim())
        annot.get_bbox_patch().set_alpha(0.4)
        annot.set_visible(False)

        def update_annot(ind):
            pos = sc.get_offsets()[ind]
            annot.xy = pos
            text = x[ind]
            annot.set_text(text)

        def hover(event):
            vis = annot.get_visible()
            if event.inaxes == ax:
                cont, index = sc.contains(event)
                if cont:
                    ind = index["ind"][0]  # Get useful value from dictionary
                    update_annot(ind)
                    annot.set_visible(True)
                    fig.canvas.draw_idle()
                else:
                    if vis:
                        annot.set_visible(False)
                        fig.canvas.draw_idle()

        canvas = FigureCanvasTkAgg(fig, container)
        canvas.draw()
        canvas.get_tk_widget().grid(row=2, column=0)
        fig.canvas.mpl_connect("motion_notify_event", hover)

        data = self.filter_filldata()

        x = [entry["date"] for entry in data]
        y = [entry["price"] for entry in data]

        x_s, y_s = zip(*sorted(zip(x, y)))
        x_s = range(len(y))

        mean = sum(map(float, y_s)) / len(list(map(float, y_s)))
        x_mean = range(len(x_s))
        y_mean = [mean for x_s in x_mean]

        FS = 14

        sc = ax.scatter(x_s, y_s, marker="o", color="red", edgecolor="black")
        ax.plot(x_mean, y_mean, linestyle="--", color="black", label="Gjennomsnitt")

        ax.set_ylabel("Literpris (Kroner/L)", fontsize=FS)
        ax.set_xticklabels([])

        ax.grid()
        ax.legend(fontsize=FS)

    def plot_station_frequency(self):
        """
        Make a pie chart showing the frequency of fills for each station.
        :return: None
        """
        data = self.filter_filldata()

        counts = {station: 0 for station in set([entry["station"] for entry in data])}
        for entry in data:
            counts[entry["station"]] += 1

        container = tk.Toplevel(self)
        container.resizable(False, False)

        # Make informative title
        msg = """Dette paidiagrammet gir ei oversikt over kvar du
        oftast har fylt opp tanken."""
        tk.Label(container, text=msg).grid(row=0, column=0)
        tk.Button(container, text="Attende", command=container.destroy, font=self.parent.font_main).grid(row=1,
                                                                                                         column=0)

        fig = Figure()
        ax = fig.add_subplot(111)
        explosions = [0.05 for i in counts.keys()]

        ax.pie(counts.values(),
               explode=explosions,
               labels=counts.keys(),
               shadow=True,
               startangle=90,
               autopct='%1.1f%%')
        ax.axis("equal")

        canvas = FigureCanvasTkAgg(fig, container)
        canvas.draw()
        canvas.get_tk_widget().grid(row=2, column=0)

    def plot_day_frequency(self):
        """
        Make a pie chart showing the frequency of fills for each day of the week.
        If no fill on a particular day, the it is omitted.
        :return: None
        """
        eng2nor = {"Mon": "Man",
                   "Tue": "Tys",
                   "Wed": "Ons",
                   "Thu": "Tor",
                   "Fri": "Fre",
                   "Sat": "Lør",
                   "Sun": "Sun"}
        nor2eng = {"Man": "Mon",
                   "Tys": "Tue",
                   "Ons": "Web",
                   "Tor": "Thu",
                   "Fre": "Fri",
                   "Lør": "Sat",
                   "Sun": "Sun"}

        data = self.filter_filldata()

        days = [eng2nor[datefromstring(entry["date"]).strftime("%a")] for entry in data]
        counts = {day: 0 for day in reversed(list(nor2eng.keys())) if day in set(days)}

        for entry in data:
            day = eng2nor[datefromstring(entry["date"]).strftime("%a")]
            counts[day] += 1

        container = tk.Toplevel(self)
        container.resizable(False, False)

        # Make informative title
        msg = """Dette paidiagrammet gir ei oversikt over kor ofte
        du fyller tanken på ulike dagar i veka."""
        tk.Label(container, text=msg).grid(row=0, column=0)
        tk.Button(container, text="Attende", command=container.destroy, font=self.parent.font_main).grid(row=1,
                                                                                                         column=0)

        fig = Figure()
        ax = fig.add_subplot(111)
        explosions = [0.05 for i in counts.keys()]

        ax.pie(counts.values(),
               explode=explosions,
               labels=counts.keys(),
               shadow=True,
               startangle=90,
               autopct='%1.1f%%')
        ax.axis("equal")

        canvas = FigureCanvasTkAgg(fig, container)
        canvas.draw()
        canvas.get_tk_widget().grid(row=2, column=0)

    def plot_day_price_variation(self):
        """
        Plot the average gas price for each day of the week in bar plot, with the standard deviation
        added to indicate the variation.
        :return: None
        """
        eng2nor = {"Mon": "Man",
                   "Tue": "Tys",
                   "Wed": "Ons",
                   "Thu": "Tor",
                   "Fri": "Fre",
                   "Sat": "Lør",
                   "Sun": "Sun"}
        nor2eng = {"Man": "Mon",
                   "Tys": "Tue",
                   "Ons": "Web",
                   "Tor": "Thu",
                   "Fre": "Fri",
                   "Lør": "Sat",
                   "Sun": "Sun"}

        data = self.filter_filldata()

        days = [eng2nor[datefromstring(entry["date"]).strftime("%a")] for entry in data]

        prices = OrderedDict({day: {"data": [], "mean": 0, "std": 0} for day in nor2eng.keys() if day in set(days)})

        for entry in data:
            day = eng2nor[datefromstring(entry["date"]).strftime("%a")]
            prices[day]["data"].append(entry["price"])

        for day in prices.keys():
            prices[day]["mean"] = sum(prices[day]["data"]) / len(prices[day]["data"])
            prices[day]["std"] = np.std(prices[day]["data"])

        # Plot data
        container = tk.Toplevel(self)
        container.resizable(False, False)

        # Make informative title
        msg = """Dette diagrammet syner den gjennomsnittlege literprisen for kvar dag i veka.
        Dersom du har to eller fleire fyllingar på ein dag, så syner diagrammet
        også standardavviket for den aktuelle dagen. Standardavviket er ein
        indikator variasjonen i datapunkta.

        Når du har registert nok data, så vil mest sannsynleg ei trend
        verte synleg der du enkelt kan sjå kva for dag som vanlegvis
        gir den lågast literprisen."""
        tk.Label(container, text=msg).grid(row=0, column=0)
        tk.Button(container, text="Attende", command=container.destroy, font=self.parent.font_main).grid(row=1,
                                                                                                         column=0)

        fig = Figure()
        ax = fig.add_subplot(111)
        FS = 14

        xs = prices.keys()
        ys = [prices[day]["mean"] for day in xs]
        stds = [prices[day]["std"] for day in xs]
        ns = [len(prices[day]["data"]) for day in xs]
        UPPER = max(ys) + 0.5
        LOWER = min(ys) - 0.5
        WIDTH = 0.8
        ax.set_ylim(LOWER, UPPER)

        ax.set_ylabel("Kroner", fontsize=FS)
        ax.tick_params(labelsize=FS)

        for day, y, std, n in zip(xs, ys, stds, ns):
            ax.bar(day, y, yerr=std, capsize=5, ec="black", linewidth=2, color="skyblue", width=WIDTH)
            ax.text(day, LOWER + 0.25, f"n = {n}", horizontalalignment="center")

        mean = sum(map(float, ys)) / len(list(map(float, ys)))
        x_mean = np.arange(-WIDTH / 2, len(xs) - WIDTH / 2, 0.01)
        y_mean = [mean for x in x_mean]
        ax.plot(x_mean, y_mean, linestyle="--", color="black", label="Gjennomsnitt")

        ax.legend(fontsize=FS)

        canvas = FigureCanvasTkAgg(fig, container)
        canvas.draw()
        canvas.get_tk_widget().grid(row=2, column=0)

    def fill_report(self):
        """
        Collect some summaries and statistics, and display for the user.
        :return: None
        """
        data = self.filter_filldata()

        container = tk.Toplevel(self)
        container.resizable(False, False)

        frame_top = tk.Frame(container)
        frame_top.grid(row=0, column=0, columnspan=2)

        frame_left = tk.Frame(container)
        frame_left.grid(row=1, column=0)

        frame_right = tk.Frame(container)
        frame_right.grid(row=1, column=1)

        tk.Label(frame_top, text="Samandrag", font=self.parent.font_heading, bg="orange").grid(row=0, column=0)

        # Button for closing report window
        tk.Button(frame_top, text="Attende", font=self.parent.font_main, command=container.destroy).grid(row=1,
                                                                                                         column=0)

        # Total number of fills
        tk.Label(frame_left, text="Total antal fyllingar: ").grid(row=1, column=0, sticky=tk.W)
        tk.Label(frame_left, text=len(data)).grid(row=1, column=1, sticky=tk.E)

        # Total cost of all fills
        tk.Label(frame_left, text="Total kostnad: ").grid(row=2, column=0, sticky=tk.W)
        total_sum = sum([float(entry["price"]) * float(entry["volume"]) for entry in data])
        tk.Label(frame_left, text=f"{self.myround(total_sum)} Kroner").grid(row=2, column=1, sticky=tk.E)

        # Lowest price
        prices = [entry["price"] for entry in data]
        tk.Label(frame_left, text="Lågaste literpris: ").grid(row=3, column=0, sticky=tk.W)
        tk.Label(frame_left, text=f"{self.myround(min(prices))} Kroner").grid(row=3, column=1, sticky=tk.E)

        # Highest price
        tk.Label(frame_left, text="Høgaste literpris: ").grid(row=4, column=0, sticky=tk.W)
        tk.Label(frame_left, text=f"{self.myround(max(prices))} Kroner").grid(row=4, column=1, sticky=tk.E)

        # Average price
        tk.Label(frame_left, text="Gjennomsnittleg literpris: ").grid(row=5, column=0, sticky=tk.W)
        tk.Label(frame_left, text=f"{self.myround(sum(prices) / len(prices))} Kroner").grid(row=5, column=1,
                                                                                            sticky=tk.E)

        # Lowest volume
        volumes = [entry["volume"] for entry in data]
        tk.Label(frame_left, text="Minste volum: ").grid(row=6, column=0, sticky=tk.W)
        tk.Label(frame_left, text=f"{self.myround(min(volumes))} liter").grid(row=6, column=1, sticky=tk.E)

        # Highest volume
        tk.Label(frame_left, text="Styrste volum: ").grid(row=7, column=0, sticky=tk.W)
        tk.Label(frame_left, text=f"{self.myround(max(volumes))} liter").grid(row=7, column=1, sticky=tk.E)

        # Average volume
        tk.Label(frame_left, text="Gjennomsnittleg volum: ").grid(row=8, column=0, sticky=tk.W)
        tk.Label(frame_left, text=f"{self.myround(sum(volumes) / len(volumes))} liter").grid(row=8, column=1,
                                                                                             sticky=tk.E)

        # Sparepotensiale. Total kostnad dersom alle fyllingane var gjort ved lågast registrerte literpris
        min_price = min(prices)
        potential_savings = self.myround(total_sum - min_price * sum([entry["volume"] for entry in data]))

        tk.Label(frame_left, text="Sparepotensiale: ").grid(row=9, column=0, sticky=tk.W)
        tk.Label(frame_left, text=f"{potential_savings} Kroner").grid(row=9, column=1, sticky=tk.E)

        # Gjennomsnittleg antal dagar mellom fyllingar
        dates = sorted([datefromstring(entry["date"]) for entry in data])
        dates_delta = [dates[i + 1] - dates[i] for i in range(len(dates) - 1)]
        avg_delta = self.myround(sum([delta.days for delta in dates_delta]) / len(dates_delta))

        tk.Label(frame_left, text="Gjennomsnittleg fyllfrekvens: ").grid(row=10, column=0, sticky=tk.W)
        tk.Label(frame_left, text=f"{avg_delta} dagar").grid(row=10, column=1, sticky=tk.E)

        # Total CO2-fotavtrykk
        footprint = self.myround(sum([entry["volume"] for entry in self.parent.data]) * 2500 / 1000000)
        tk.Label(frame_left, text="Total CO2-fotavtrykk: ").grid(row=11, column=0, sticky=tk.W)
        tk.Label(frame_left, text=f"{footprint} tonn CO2").grid(row=11, column=1, sticky=tk.E)

    def filter_filldata(self, year=datetime.MINYEAR, month=1, day=1):
        """
        Include only fill data starting from the provided start date.
        :param year: int
        :param month: int
        :param day: int
        :return: list, filtered to include only data starting from provided start time
        """
        return list(
            filter(lambda fill: datefromstring(fill["date"]) >= datetime.date(year, month, day), self.parent.data))

    @staticmethod
    def myround(n, k=2):
        """Simple rounding routine to guarantee that a float is displayed with two decimals.
        Only meant to be used in the fill report method for presenting statistics.

        Returns : float or str"""
        rounded = round(n, k)
        decimals = str(rounded).split(".")[1]
        if len(decimals) < k:
            return str(rounded) + "0"
        else:
            return rounded


class FilterDateToolBar(tk.Frame):
    def __init__(self, parent, row, column):
        """
        Toolbar for setting year, month, and day for filtering the fill data.

        Provide the row and column for where to place the frame
        :param parent: parent widget for the toolbar
        :param row: int
        :param column: int
        """
        tk.Frame.__init__(self)

        self.parent = parent
        self.parent.dbug("OPENING DATA FILTER", h=True)
        self.row = row
        self.column = column

        self.grid(row=self.row, column=self.column)

        tk.Label(self, text="År: ").grid(row=0, column=0)
        tk.Label(self, text="Månad: ").grid(row=0, column=1)
        tk.Label(self, text="Dag: ").grid(row=0, column=2)


def datefromstring(str):
    """
    Helper function. Take a date string of the format 'yyyy-mm-dd'
    and return a datetime.date object
    :param str: yyyy-mm-dd
    :return: datetime.date
    """
    return datetime.date(*list(map(int, str.split("-"))))


def edit_help(index, rootdir):
    """
    Display help messages for adding or editing fill data.
    :param index: the index of the tk.Button that is put into the EditFills window.
    :return: InfoBox instance
    """
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

        image = ImageTk.PhotoImage(Image.open(os.path.join(rootdir, "Bilete", "help_volum.jpg")))
        return InfoBox(msg, image)
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
        image = ImageTk.PhotoImage(Image.open(os.path.join(rootdir, "Bilete", "help_price.jpg")))
        return InfoBox(msg, image)
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
        image = ImageTk.PhotoImage(Image.open(os.path.join(rootdir, "Bilete", "help_date.jpg")))
        return InfoBox(msg, image)
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
        image = ImageTk.PhotoImage(Image.open(os.path.join(rootdir, "Bilete", "help_time.jpg")))
        return InfoBox(msg, image)
    elif index == 5:
        msg = """
        Her kan du skrive inn ein 
        kommentar om fyllinga. Til dømes 
        kan du skrive 'Ferietur juli 2019',
        for å halde styr på drivstofforbruket
        for ein lang køyretur.
        """
        image = ImageTk.PhotoImage(Image.open(os.path.join(rootdir, "Bilete", "help_station.jpg")))
        return InfoBox(msg, image)
    elif index == 6:
        msg = """
        Her veljer du det bonusprogrammet du brukte.
        Dersom du ikkje brukde noko bonusprogram,
        så veljer du "Ingen bonus".

        Hugs at somme bonusprogram ikkje er 
        kompatible med somme stasjonar. Pass
        på at du veljer korrekte kombinasjonar.
        """
        image = ImageTk.PhotoImage(Image.open(os.path.join(rootdir, "Bilete", "help_bonus.jpg")))
        return InfoBox(msg, image)

    elif index == 7:
        msg = """
        Her veljer du bensinstasjonen der
        du fylte drivstoff. Dersom kjeden
        ikkje er lagt inn i Gassy, så send
        ein e-post og etterspør kjeden.

        anders.brakestad@gmail.com
        """
        image = ImageTk.PhotoImage(Image.open(os.path.join(rootdir, "Bilete", "help_station.jpg")))
        return InfoBox(msg, image)


def current_time():
    return str(datetime.datetime.now().time()).split(".")[0]

def current_date():
    return f"{datetime.datetime.now().year}{datetime.datetime.now().month}{datetime.datetime.now().day}"


if __name__ == "__main__":
    app = Gassy()
    app.resizable(False, False)
    app.title(app.name)
    app.mainloop()

    if app.automatic_backup.get():
        app.backup()
    else:
        app.dbug("DID NOT BACK UP DATA", h=True)
    app.dbug("CLOSING GASSY", h=True)
    app.dbug(None, h=True)