import locale

from django.db import models
from django.utils.html import format_html


class Adresse(models.Model):
    id = models.AutoField(primary_key=True)
    strasse = models.CharField(max_length=512, verbose_name="Straße und Hausnummer")
    plz = models.CharField(max_length=5, verbose_name="PLZ")
    ort = models.CharField(max_length=512, verbose_name="Ort")
    entfernung = models.IntegerField(verbose_name="Entfernung (km)", help_text="Entfernung in km")

    def __str__(self):
        str = self.str_kurz()
        if self.entfernung is not None:
            # zusätzlich die Entfernung in Klammern mit ausgeben
            str += f" ({self.entfernung} km)"
        return str

    def str_kurz(self):
        return f"{self.strasse}, {self.plz} {self.ort}"

    class Meta:
        verbose_name = "Adresse"
        verbose_name_plural = " Adressen"
        ordering = ['plz']


class Kunde(models.Model):
    id = models.AutoField(primary_key=True)
    anrede = models.CharField(max_length=20, blank=True, null=True)
    vorname = models.CharField(max_length=200, blank=True, null=True)
    nachname = models.CharField(max_length=200)
    adresse = models.ForeignKey(Adresse, blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        str = self.str_kurz()
        if self.adresse is not None:
            # zusätzlich die Adresse in Klammern mit ausgeben
            str += f" ({self.adresse.ort}, {self.adresse.strasse})"
        return str

    def str_kurz(self):
        if self.vorname is not None:
            return f"{self.nachname}, {self.vorname}"
        else:
            return f"{self.nachname}"

    class Meta:
        verbose_name = "Kunde"
        verbose_name_plural = "  Kunden"
        ordering = ['nachname', 'vorname']


class Fahrt(models.Model):
    id = models.AutoField(primary_key=True)
    fahrt_nr = models.IntegerField(blank=True, null=True)
    datum = models.DateField()
    kunde = models.ForeignKey(Kunde, blank=True, null=True, on_delete=models.SET_NULL)
    adresse = models.ForeignKey(Adresse, blank=True, null=True,
                                on_delete=models.SET_NULL,
                                help_text="Die Ziel Adresse, wird bei Neueingabe der Fahrt automatisch gefüllt. "
                                          "Zusätzlich gespeichert, "
                                          "da der Kunde umziehen kann.")
    entfernung = models.IntegerField(blank=True, null=True,
                                     verbose_name="Entfernung (km)",
                                     help_text="Entferung in km, wird bei Neueingabe der Fahrt automatisch gefüllt. "
                                               "Zusätzlich gespeichert, "
                                               "da sich die Entfernung z.B. eigenem bei Umzug ändern kann.")
    betrag = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    steuer = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    konto = models.CharField(max_length=100, blank=True, null=True)
    kommentar = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.str_detaliert()

    def str_detaliert(self):
        return f"Datum: {self.datum.strftime('%d.%m.%Y')}; " \
               f"Kunde: {self.kunde.str_kurz() if self.kunde else ''}; " \
               + self.str_ziel()

    def str_ziel(self):
        return f"Adresse: {self.adresse.str_kurz() if self.adresse else ''}; " \
               f"Entfernung: {self.entfernung} km"

    def str_adresse_kurz(self):
        if self.adresse is not None:
            if self.adresse.entfernung != self.entfernung:
                title = "Die Entfernung der Fahrt weicht von der Entfernung der Adresse ab."
                return format_html(f"{self.adresse.str_kurz()}. "
                                   f"<span title='{title}' style='color: red;'> ({self.adresse.entfernung} km)</span>")
            else:
                return f"{self.adresse.str_kurz()}"
        return ""

    def str_entfernung(self):
        if self.adresse is not None:
            if self.adresse.entfernung != self.entfernung:
                title = "Die Entfernung weicht von der Entfernung der Adresse ab."
                return format_html(f"<span title='{title}' style='color: red;'>{self.entfernung}</span>")
            else:
                return str(self.entfernung)
        return str(self.entfernung)

    str_adresse_kurz.allow_tags = True

    class Meta:
        verbose_name = "Fahrt"
        verbose_name_plural = "   Fahrten"
        ordering = ['-datum', '-id', 'kommentar']


class Einstellung(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    wert_date = models.DateField(null=True, blank=True)
    wert_char = models.CharField(max_length=255, null=True, blank=True)
    wert_decimal = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.name + ": " + self.wert

    @property
    def wert(self):
        werte = list()
        if self.wert_date:
            werte.append(self.wert_date)
        if self.wert_char:
            werte.append(self.wert_char)
        if self.wert_decimal:
            werte.append(self.wert_decimal)
        if len(werte) > 1:
            raise RuntimeError(
                f"Der Wert der Einstellung '{self.name}' ist nicht eindeutig, es darf nur ein Wert angegeben werden.")
        return werte[0] if len(werte) == 1 else None

    class Meta:
        verbose_name = "Einstellung"
        verbose_name_plural = "Einstellungen"
        ordering = ['name']
