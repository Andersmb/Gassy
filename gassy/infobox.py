from mywidgets import *


class InfoBox(tk.Toplevel):
    def __init__(self, app, msg, image):
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

        label_image = MyLabel(frame_left, image=self.image)
        label_image.grid(row=0, column=0, sticky=tk.N)
        label_image.image = self.image

        textbox = MyText(frame_right, width=40, height=12)
        textbox.grid(row=0, column=0, sticky=tk.NSEW)
        textbox.insert(tk.END, self.msg)
        textbox.config(state=tk.DISABLED)

        MyButton(frame_left, text="Den er grei!", command=self.destroy).grid(row=1, column=0)