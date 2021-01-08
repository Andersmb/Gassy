import tkinter as tk
from tkinter import messagebox
import json
from copy import deepcopy
import os

from mywidgets import *
from helpers import *
from mycars import MyCars
from mainwindow import MainWindow
from feedback import Feedback
from settings import Settings
from editfills import EditFills
from addfill import AddFill
from analysis import Analysis


DEV = False
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
        self.rootdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.d_project = os.path.join(os.path.expanduser("~"), self.name)
        self.d_backups = os.path.join(self.d_project, "Sikkerheitskopiar")
        self.f_settings = os.path.join(self.d_project, "Innstillingar.json")
        self.f_data = os.path.join(self.d_project, "Fyllingsdata.json")
        self.f_cars = os.path.join(self.d_project, "Mine_bilar.json")

        # Initialize variables
        self.bonus = tk.StringVar()
        self.station = tk.StringVar()
        self.automatic_backup = tk.BooleanVar()
        self.selected_car = tk.StringVar()

        # Define the gas station options and bonus options
        self.stations = ["Circle K", "Shell", "Best", "Uno-X", "Esso", "OKQ8", "Ukjend"]
        self.bonuses = ["Trumf", "Coop", "Ingen bonus", "Ukjend"]

        # Set default values for station and bonus
        self.bonus.set(self.bonuses[0])
        self.station.set(self.stations[0])

        # Define default user settings
        self.defaults = {
            "automatic_backup": False
        }

        # Load settings
        self.current_settings = self.load_settings()
        self.set_system_variables()

        # Load data
        self.data = self.load_data()

        # Load cars
        self.cars = self.load_cars()

        # Initialize the main window
        self.mainwindow = MainWindow(self)
        self.show_main(self)
        self.startup = False

    def show_main(self, windowtoforget):
        self.mainwindow.grid(row=0, column=0)
        if not self.startup:
            windowtoforget.grid_forget()

    def show_addfill(self):
        self.addfill = AddFill(self)
        self.mainwindow.grid_forget()
        self.addfill.grid(row=0, column=0)

    def show_editfills(self):
        self.editfills = EditFills(self)
        self.mainwindow.grid_forget()
        self.editfills.grid(row=0, column=0)

    def show_feedback(self):
        self.feedback = Feedback(self)
        self.mainwindow.grid_forget()
        self.feedback.grid(row=0, column=0)

    def show_analysis(self):
        if len(self.data) == 0:
            msg = """Du har ikkje registrert fyllingar endå, så denne funksjonaliteten vil ikkje fungere skikkeleg."""
            messagebox.showwarning(self.name, msg)
        self.analysis = Analysis(self)
        self.mainwindow.grid_forget()
        self.analysis.grid(row=0, column=0)

    def show_settings(self):
        self.settings = Settings(self)
        self.mainwindow.grid_forget()
        self.settings.grid(row=0, column=0)

    def show_mycars(self):
        self.mycars = MyCars(self)
        self.mainwindow.grid_forget()
        self.mycars.grid(row=0, column=0)

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

    def load_cars(self):
        """
        Look for file containing user's cars, and read the contents.
        :return:
        """
        self.dbug("LOADING CARS", h=True)
        try:
            self.dbug("Looking for cars file...")
            with open(self.f_cars) as f:
                cars = json.load(f)
                self.dbug("...file found.")
                return cars
        except FileNotFoundError:
            self.dbug("...file not found. Making new one.")
            open(self.f_cars, "w").close()
            return []
        except json.decoder.JSONDecodeError:
            self.dbug("...empty file found.")
            return []

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

    def dump_cars(self):
        self.dbug("DUMPING CARS", h=True)
        with open(self.f_cars, "w") as f:
            json.dump(self.cars, f, indent=4)
        self.dbug("...dumped")
        self.cars = self.load_cars()
        self.dbug("...cars reloaded")

    def dump_data(self):
        self.dbug("DUMPING DATA", h=True)
        with open(self.f_data, "w") as f:
            json.dump(self.data, f, indent=4)
        self.dbug("...dumped")
        self.data = self.load_data()
        self.dbug("...data reloaded")

    def not_implemented(self):
        return messagebox.showerror(self.name, "Dette er ikkje implementert endå :(")


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
