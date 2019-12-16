import tkinter as tk

from mywidgets import MyButton, MyLabel, MyHeading, MyEntry


class MyCars(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self)
        self.parent = parent
        self.parent.dbug("MY CARS", h=True)
        self.padx = 20
        self.pady = 5

        self.make = tk.StringVar()
        self.model = tk.StringVar()
        self.year = tk.StringVar()
        self.nick = tk.StringVar()

        self.place_widgets()

    def place_widgets(self):
        ROW = 0
        self.frame_l = tk.Frame(self)
        self.frame_l.grid(row=0, column=0)
        self.frame_r = tk.Frame(self)
        self.frame_r.grid(row=0, column=1)

        # Heading
        MyHeading(self.frame_l, text="Mine bilar").grid(row=0, column=0, sticky=tk.W, pady=self.pady, padx=self.padx)

        MyLabel(self.frame_r, text="Merke:").grid(row=0, column=0, sticky=tk.W, pady=self.pady, padx=self.padx/2)
        MyLabel(self.frame_r, text="Modell:").grid(row=1, column=0, sticky=tk.W, pady=self.pady, padx=self.padx/2)
        MyLabel(self.frame_r, text="Årsmodell:").grid(row=2, column=0, sticky=tk.W, pady=self.pady, padx=self.padx/2)
        MyLabel(self.frame_r, text="Kallenamn:", width=10).grid(row=3, column=0, sticky=tk.W, pady=self.pady, padx=self.padx/2)

        self.l_make = MyLabel(self.frame_r, textvariable=self.make).grid(row=0, column=1, sticky=tk.W, pady=self.pady, padx=self.padx/2)
        self.l_model = MyLabel(self.frame_r, textvariable=self.model).grid(row=1, column=1, sticky=tk.W, pady=self.pady, padx=self.padx/2)
        self.l_year = MyLabel(self.frame_r, textvariable=self.year).grid(row=2, column=1, sticky=tk.W, pady=self.pady, padx=self.padx/2)
        self.l_nick = MyLabel(self.frame_r, textvariable=self.nick).grid(row=3, column=1, sticky=tk.W, pady=self.pady, padx=self.padx/2)

        # Car Labels
        for nick, ROW in zip(sorted([car["kallenamn"] for car in self.parent.cars]),
                             range(len(self.parent.cars))):
            MyButton(self.frame_l,
                     text=nick,
                     fg="blue",
                     command=lambda nick=nick: self.show_car_info(nick)).grid(row=ROW + 1, column=0, sticky=tk.W,
                                                                              pady=self.pady,
                                                                              padx=self.padx)

        MyButton(self.frame_l,
                 text="Legg til ny bil",
                 command=self.add_new_car).grid(row=ROW+2, column=0, sticky=tk.W, pady=self.pady, padx=self.padx)

        MyButton(self.frame_l,
                 text="Slett bil",
                 command=self.delete_car).grid(row=ROW+3, column=0, sticky=tk.W, pady=self.pady, padx=self.padx)

        MyButton(self.frame_l,
                 text="Attende",
                 command=lambda: self.parent.show_main(self)).grid(row=ROW+4,
                                                                   column=0,
                                                                   sticky=tk.W, padx=self.padx, pady=self.pady)

    def update_widgets(self):
        self.frame_l.grid_forget()
        self.frame_r.grid_forget()
        self.place_widgets()

    def show_car_info(self, nick):
        car = self.get_car_from_nickname(nick)
        self.make.set(car["merke"])
        self.model.set(car["modell"])
        self.year.set(car["årsmodell"])
        self.nick.set(car["kallenamn"])

    def get_car_from_nickname(self, nick):
        for car in self.parent.cars:
            if car["kallenamn"] == nick:
                return car
        else:
            raise Exception(f"Car with nickname {nick} not found.")

    def add_new_car(self):
        root = tk.Toplevel(self)

        MyLabel(root, text="Merke:").grid(row=0, column=0, sticky=tk.W, pady=self.pady, padx=self.padx)
        MyLabel(root, text="Modell:").grid(row=1, column=0, sticky=tk.W, pady=self.pady, padx=self.padx)
        MyLabel(root, text="Årsmodell:").grid(row=2, column=0, sticky=tk.W, pady=self.pady, padx=self.padx)
        MyLabel(root, text="Kallenamn:").grid(row=3, column=0, sticky=tk.W, pady=self.pady, padx=self.padx)

        l_make = MyEntry(root)
        l_make.grid(row=0, column=1, sticky=tk.W, pady=self.pady, padx=self.padx)
        l_model = MyEntry(root)
        l_model.grid(row=1, column=1, sticky=tk.W, pady=self.pady, padx=self.padx)
        l_year = MyEntry(root)
        l_year.grid(row=2, column=1, sticky=tk.W, pady=self.pady, padx=self.padx)
        l_nick = MyEntry(root)
        l_nick.grid(row=3, column=1, sticky=tk.W, pady=self.pady, padx=self.padx)

        l_make.focus_set()

        def add_car():
            new_car = {}
            new_car["merke"] = l_make.get()
            new_car["modell"] = l_model.get()
            new_car["årsmodell"] = l_year.get()
            new_car["kallenamn"] = l_nick.get()

            # Update text variables
            self.make.set(new_car["merke"])
            self.model.set(new_car["modell"])
            self.year.set(new_car["årsmodell"])
            self.nick.set(new_car["kallenamn"])

            # Create new car and update window
            self.parent.cars.append(new_car)
            self.parent.dump_cars()
            self.update_widgets()
            root.destroy()

        MyButton(root, text="Legg til", command=add_car).grid(row=4,
                                                              column=0, sticky=tk.W, pady=self.pady, padx=self.padx)
        MyButton(root, text="Avbryt ",
                 command=root.destroy).grid(row=5, column=0, sticky=tk.W, pady=self.pady, padx=self.padx)

    def delete_car(self):
        nick = self.nick.get()
        self.parent.dbug(f"Attempting to delete car: {nick}")
        for i, car in enumerate(self.parent.cars):
            if car["kallenamn"] == nick:
                self.parent.dbug("...match found")
                del self.parent.cars[i]

                # Update text variables
                self.parent.dbug("...resetting text variables")
                self.make.set("")
                self.model.set("")
                self.year.set("")
                self.nick.set("")
                self.update_widgets()

                self.parent.dump_cars()