from mywidgets import *
from tkinter import messagebox


class Settings(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self)
        self.parent = parent
        self.parent.dbug("OPENING SETTINGS", h=True)

        self.grid(row=0, column=0, sticky=tk.NSEW)

        self.frame = tk.Frame(self)
        self.frame.grid(row=0, column=0)

        # Labels
        MyHeading(self.frame, text="Innstillingar").grid(row=0, column=0, sticky=tk.W)
        MyLabel(self.frame, text=f"Prosjektmappe for {self.parent.name}:").grid(row=1, column=0, sticky=tk.W)
        MyLabel(self.frame, text=self.parent.d_project).grid(row=1, column=1, sticky=tk.W)
        MyLabel(self.frame, text="Datafil:").grid(row=2, column=0, sticky=tk.W)
        MyLabel(self.frame, text=self.parent.f_data).grid(row=2, column=1, sticky=tk.W)
        MyLabel(self.frame, text="Innstillingsfil:").grid(row=3, column=0, sticky=tk.W)
        MyLabel(self.frame, text=self.parent.f_settings).grid(row=3, column=1, sticky=tk.W)
        MyLabel(self.frame, text="Mappe for sikkerheitskopiar:").grid(row=4, column=0, sticky=tk.W)
        MyLabel(self.frame, text=self.parent.d_backups).grid(row=4, column=1, sticky=tk.W)

        # Check buttons
        MyCheckbutton(self.frame, text=f"Automatisk sikkerheitskopi når du avsluttar {self.parent.name}?",
                       variable=self.parent.automatic_backup).grid(row=5, column=0, sticky=tk.W)

        # Buttons
        MyButton(self.frame, text="Ta sikkerheitskopi",
                 command=self.parent.backup).grid(row=6, column=0, sticky=tk.W)
        MyButton(self.frame, text="Lagre innstillingar",
                 command=self.get_new_settings).grid(row=7, column=0, sticky=tk.W)
        MyButton(self.frame, text="Attende",
                 command=lambda: self.parent.show_main(self)).grid(row=8, column=0, sticky=tk.W)

    def get_new_settings(self):
        self.parent.current_settings["automatic_backup"] = self.parent.automatic_backup.get()

        self.parent.set_system_variables()
        self.parent.dump_settings()

        tk.messagebox.showinfo(self.parent.name, f"Innstillingar lagra i {self.parent.f_settings}")