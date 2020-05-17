from django.db import models


class Adresse(models.Model):
    id = models.AutoField(primary_key=True)
    strasse = models.CharField(max_length=512, verbose_name="Straße")
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
        verbose_name_plural = "Adressen"
        ordering = ['plz']


class Kunde(models.Model):
    id = models.AutoField(primary_key=True)
    anrede = models.CharField(max_length=20, blank=True, null=True)
    vorname = models.CharField(max_length=200)
    nachname = models.CharField(max_length=200, blank=True, null=True)
    adresse = models.ForeignKey(Adresse, blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        str = self.str_kurz()
        if self.adresse is not None:
            # zusätzlich die Adresse in Klammern mit ausgeben
            str += f" ({self.adresse.ort}, {self.adresse.strasse})"
        return str

    def str_kurz(self):
        return f"{self.nachname}, {self.vorname}"

    class Meta:
        verbose_name = "Kunde"
        verbose_name_plural = "Kunden"
        ordering = ['nachname', 'vorname']


class Fahrt(models.Model):
    id = models.AutoField(primary_key=True)
    fahrt_nr = models.IntegerField(blank=True, null=True)
    datum = models.DateField()
    kunde = models.ForeignKey(Kunde, blank=True, null=True, on_delete=models.SET_NULL)
    adresse = models.ForeignKey(Adresse, blank=True, null=True,
                                on_delete=models.SET_NULL,
                                help_text="Die Ziel Adresse. Zusätzlich gespeichert, da der Kunde umziehen kann.")
    entfernung = models.IntegerField(blank=True, null=True,
                                     help_text="Entferung in km. Zusätzlich gespeichert, "
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

    class Meta:
        verbose_name = "Fahrt"
        verbose_name_plural = "Fahrten"
        ordering = ['-datum', '-id', 'kommentar']
