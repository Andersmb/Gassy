import smtplib
from tkinter import messagebox

from mywidgets import *


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
        MyHeading(self, text="Gi tilbakemelding").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)

        # Choose subject
        tk.OptionMenu(self, self.subject, *self.subject_options).grid(row=1, sticky=tk.W, padx=10, pady=5)

        # Main body
        MyLabel(self, text="Skriv di tilbakemelding her").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)

        self.body = MyText(self)
        self.body.grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        self.body.focus_set()

        MyButton(self,
                  text="Send tilbakemelding",
                  command=self.send_feedback).grid(row=4, column=0, sticky=tk.W, padx=10, pady=5)
        MyButton(self,
                  text="Attende",
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
            server.sendmail(self.mail, self.mail, msg.encode('utf-8'))
            messagebox.showinfo(self.parent.name, "Tusen takk for tilbakemeldinga! :)")
        else:
            tk.messagebox.showwarning(self.parent.name, "Du har ikkje skrive noko i tekstboksen.")