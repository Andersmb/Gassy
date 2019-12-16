import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from collections import OrderedDict

from mywidgets import *
from helpers import *


class Analysis(tk.Frame):
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
        self.padx = 5
        self.pady = 5

        self.grid(row=0, column=0)

        frame_left = tk.Frame(self)
        frame_right = tk.Frame(self)
        frame_left.grid(row=0, column=0)
        frame_right.grid(row=0, column=1)

        image = ImageTk.PhotoImage(Image.open(os.path.join(self.parent.rootdir, "Bilete", "graphing.jpg")))
        label_image = MyLabel(frame_left, image=image)
        label_image.image = image
        label_image.grid(row=0, column=0)

        MyHeading(frame_right, text="Analyse av fyllingsdata").grid(row=0, column=0, sticky=tk.N, padx=self.padx, pady=self.pady)

        MyButton(frame_right, text="Attende",
                  command=lambda: self.parent.show_main(self)).grid(row=1, column=0, padx=self.padx, pady=self.pady, sticky=tk.W)
        MyButton(frame_right, text="Korleis har literprisen variert?",
                  command=self.plot_price).grid(row=2, column=0, padx=self.padx, pady=self.pady, sticky=tk.W)
        MyButton(frame_right, text="Kvar har eg fylt drivstoff oftast?",
                  command=self.plot_station_frequency).grid(row=3, column=0, padx=self.padx, pady=self.pady, sticky=tk.W)
        MyButton(frame_right, text="På kva dag fyller eg oftast?",
                  command=self.plot_day_frequency).grid(row=4, column=0, padx=self.padx, pady=self.pady, sticky=tk.W)
        MyButton(frame_right, text="Samandrag",
                  command=self.fill_report).grid(row=5, column=0, padx=self.padx, pady=self.pady, sticky=tk.W)

        MyButton(frame_right, text="Literpris for ulike dagar",
                  command=self.plot_day_price_variation).grid(row=6, column=0, padx=self.padx, pady=self.pady, sticky=tk.W)

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
        MyLabel(container, text=msg).grid(row=0, column=0, padx=self.padx, pady=self.pady)
        MyButton(container, text="Attende", command=container.destroy).grid(row=1, column=0, padx=self.padx,
                                                                            pady=self.pady)

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

        data = self.parent.data

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
        data = self.parent.data

        counts = {station: 0 for station in set([entry["station"] for entry in data])}
        for entry in data:
            counts[entry["station"]] += 1

        container = tk.Toplevel(self)
        container.resizable(False, False)

        # Make informative title
        msg = """Dette paidiagrammet gir ei oversikt over kvar du
        oftast har fylt opp tanken."""
        MyLabel(container, text=msg).grid(row=0, column=0, padx=self.padx, pady=self.pady)
        MyButton(container, text="Attende", command=container.destroy).grid(row=1, column=0, padx=self.padx,
                                                                            pady=self.pady)

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

        data = self.parent.data

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
        MyLabel(container, text=msg).grid(row=0, column=0, padx=self.padx, pady=self.pady)
        MyButton(container, text="Attende", command=container.destroy).grid(row=1, column=0, padx=self.padx, pady=self.pady)

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

        data = self.parent.data

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
        MyLabel(container, text=msg).grid(row=0, column=0, padx=self.padx, pady=self.pady)
        MyButton(container, text="Attende", command=container.destroy).grid(row=1, column=0, padx=self.padx,
                                                                            pady=self.pady)

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
        data = self.parent.data

        container = tk.Toplevel(self)
        container.resizable(False, False)

        frame_top = tk.Frame(container)
        frame_top.grid(row=0, column=0, columnspan=2)

        frame_left = tk.Frame(container)
        frame_left.grid(row=1, column=0)

        frame_right = tk.Frame(container)
        frame_right.grid(row=1, column=1)

        MyHeading(frame_top, text="Samandrag").grid(row=0, column=0, padx=self.padx, pady=self.pady)
        MyButton(frame_top, text="Attende", command=container.destroy).grid(row=1, column=0, padx=self.padx,
                                                                            pady=self.pady)

        # Total number of fills
        MyLabel(frame_left, text="Total antal fyllingar: ").grid(row=1, column=0, sticky=tk.W, padx=self.padx, pady=self.pady)
        MyLabel(frame_left, text=len(data)).grid(row=1, column=1, sticky=tk.E, padx=self.padx, pady=self.pady)

        # Total cost of all fills
        MyLabel(frame_left, text="Total kostnad: ").grid(row=2, column=0, sticky=tk.W, padx=self.padx, pady=self.pady)
        total_sum = sum([float(entry["price"]) * float(entry["volume"]) for entry in data])
        MyLabel(frame_left, text=f"{self.myround(total_sum)} Kroner").grid(row=2, column=1, sticky=tk.E, padx=self.padx, pady=self.pady)

        # Lowest price
        prices = [entry["price"] for entry in data]
        MyLabel(frame_left, text="Lågaste literpris: ").grid(row=3, column=0, sticky=tk.W, padx=self.padx, pady=self.pady)
        MyLabel(frame_left, text=f"{self.myround(min(prices))} Kroner").grid(row=3, column=1, sticky=tk.E, padx=self.padx, pady=self.pady)

        # Highest price
        MyLabel(frame_left, text="Høgaste literpris: ").grid(row=4, column=0, sticky=tk.W, padx=self.padx, pady=self.pady)
        MyLabel(frame_left, text=f"{self.myround(max(prices))} Kroner").grid(row=4, column=1, sticky=tk.E, padx=self.padx, pady=self.pady)

        # Average price
        MyLabel(frame_left, text="Gjennomsnittleg literpris: ").grid(row=5, column=0, sticky=tk.W, padx=self.padx, pady=self.pady)
        MyLabel(frame_left, text=f"{self.myround(sum(prices) / len(prices))} Kroner").grid(row=5,
                                                                                           column=1,
                                                                                           sticky=tk.E, padx=self.padx, pady=self.pady)

        # Lowest volume
        volumes = [entry["volume"] for entry in data]
        MyLabel(frame_left, text="Minste volum: ").grid(row=6, column=0, sticky=tk.W, padx=self.padx, pady=self.pady)
        MyLabel(frame_left, text=f"{self.myround(min(volumes))} liter").grid(row=6, column=1, sticky=tk.E, padx=self.padx, pady=self.pady)

        # Highest volume
        MyLabel(frame_left, text="Styrste volum: ").grid(row=7, column=0, sticky=tk.W, padx=self.padx, pady=self.pady)
        MyLabel(frame_left, text=f"{self.myround(max(volumes))} liter").grid(row=7, column=1, sticky=tk.E, padx=self.padx, pady=self.pady)

        # Average volume
        MyLabel(frame_left, text="Gjennomsnittleg volum: ").grid(row=8, column=0, sticky=tk.W, padx=self.padx, pady=self.pady)
        MyLabel(frame_left, text=f"{self.myround(sum(volumes) / len(volumes))} liter").grid(row=8, column=1,
                                                                                             sticky=tk.E, padx=self.padx, pady=self.pady)

        # Sparepotensiale. Total kostnad dersom alle fyllingane var gjort ved lågast registrerte literpris
        min_price = min(prices)
        potential_savings = self.myround(total_sum - min_price * sum([entry["volume"] for entry in data]))

        MyLabel(frame_left, text="Sparepotensiale: ").grid(row=9, column=0, sticky=tk.W, padx=self.padx, pady=self.pady)
        MyLabel(frame_left, text=f"{potential_savings} Kroner").grid(row=9, column=1, sticky=tk.E, padx=self.padx, pady=self.pady)

        # Gjennomsnittleg antal dagar mellom fyllingar
        dates = sorted([datefromstring(entry["date"]) for entry in data])
        dates_delta = [dates[i + 1] - dates[i] for i in range(len(dates) - 1)]
        avg_delta = self.myround(sum([delta.days for delta in dates_delta]) / len(dates_delta))

        MyLabel(frame_left, text="Gjennomsnittleg fyllfrekvens: ").grid(row=10, column=0, sticky=tk.W, padx=self.padx, pady=self.pady)
        MyLabel(frame_left, text=f"{avg_delta} dagar").grid(row=10, column=1, sticky=tk.E, padx=self.padx, pady=self.pady)

        # Total CO2-fotavtrykk
        footprint = self.myround(sum([entry["volume"] for entry in self.parent.data]) * 2500 / 1000000)
        MyLabel(frame_left, text="Total CO2-fotavtrykk: ").grid(row=11, column=0, sticky=tk.W, padx=self.padx, pady=self.pady)
        MyLabel(frame_left, text=f"{footprint} tonn CO2").grid(row=11, column=1, sticky=tk.E, padx=self.padx, pady=self.pady)

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