import datetime
from PIL import Image, ImageTk
import os

from infobox import InfoBox


def datefromstring(str):
    """
    Helper function. Take a date string of the format 'yyyy-mm-dd'
    and return a datetime.date object
    :param str: yyyy-mm-dd
    :return: datetime.date
    """
    return datetime.date(*list(map(int, str.split("-"))))


def edit_help(app, index, rootdir):
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
        return InfoBox(app, msg, image)
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
        return InfoBox(app, msg, image)
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
        return InfoBox(app, msg, image)
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
        return InfoBox(app, msg, image)
    elif index == 5:
        msg = """
        Her kan du skrive inn ein 
        kommentar om fyllinga. Til dømes 
        kan du skrive 'Ferietur juli 2019',
        for å halde styr på drivstofforbruket
        for ein lang køyretur.
        """
        image = ImageTk.PhotoImage(Image.open(os.path.join(rootdir, "Bilete", "help_station.jpg")))
        return InfoBox(app, msg, image)
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
        return InfoBox(app, msg, image)

    elif index == 7:
        msg = """
        Her veljer du bensinstasjonen der
        du fylte drivstoff. Dersom kjeden
        ikkje er lagt inn i Gassy, så send
        ein e-post og etterspør kjeden.

        anders.brakestad@gmail.com
        """
        image = ImageTk.PhotoImage(Image.open(os.path.join(rootdir, "Bilete", "help_station.jpg")))
        return InfoBox(app, msg, image)


def current_time():
    return str(datetime.datetime.now().time()).split(".")[0]


def current_date():
    return f"{datetime.datetime.now().year}{datetime.datetime.now().month}{datetime.datetime.now().day}"