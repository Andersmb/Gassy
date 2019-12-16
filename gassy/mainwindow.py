from mywidgets import *
from PIL import Image, ImageTk
import os


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

        MyHeading(frame_right,
                 text="Velkommen til Gassy!").grid(row=0, column=0, sticky=tk.EW, padx=20, pady=10)

        MyButton(frame_right,
                  text="Legg til ny fylling",
                  fg="green",
                  command=self.parent.show_addfill).grid(row=1, column=0, sticky=tk.EW, padx=20, pady=5)

        MyButton(frame_right,
                  text="Mine fyllingar",
                  command=self.parent.show_editfills).grid(row=2, column=0, sticky=tk.EW, padx=20, pady=5)

        MyButton(frame_right,
                  text="Mine analysar",
                  command=self.parent.show_analysis).grid(row=3, column=0, sticky=tk.EW, padx=20, pady=5)

        MyButton(frame_right,
                  text="Mine innstillingar",
                  command=self.parent.show_settings).grid(row=4, column=0, sticky=tk.EW, padx=20, pady=5)

        MyButton(frame_right,
                  text="Ris og ros",
                  command=self.parent.show_feedback).grid(row=5, column=0, sticky=tk.EW, padx=20, pady=5)

        MyButton(frame_right,
                  text="Mine bilar",
                  command=self.parent.show_mycars).grid(row=6, column=0, sticky=tk.EW, padx=20, pady=5)

        MyButton(frame_right,
                  text="Avslutt",
                  command=self.parent.destroy).grid(row=7, column=0, sticky=tk.EW, padx=20, pady=5)

        if len(self.parent.data) == 0:
            MyLabel(self.frame_left, text="Datafila di er tom", fg="red").grid(row=1, column=0)
        else:
            if len(self.parent.data) > 1:
                MyLabel(self.frame_left,
                        text=f"Datafila di har {len(self.parent.data)} fyllingar :)",
                        fg="green").grid(row=1, column=0)
            else:
                MyLabel(self.frame_left,
                        text=f"Datafila di har {len(self.parent.data)} fylling :)",
                        fg="green").grid(row=1, column=0)

        if len(self.parent.cars) == 0:
            MyLabel(self.frame_left, text="Ingen bilar er registrert", fg="red").grid(row=2, column=0)

    def refresh_data(self):
        self.parent.data = self.parent.load_data()
        image = ImageTk.PhotoImage(Image.open(os.path.join(self.parent.rootdir, "Bilete", "frontpage_gassy_small_green.jpg")))
        label = MyLabel(self.frame_left, image=image)
        label.image = image
        label.grid(row=0, column=0, sticky=tk.E)
        self.after(500, lambda: self.__init__(self.parent))