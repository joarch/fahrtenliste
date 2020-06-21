import datetime
import json

from django.core import serializers
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils.html import format_html

from fahrtenliste_main.format_util import json_serial


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

    def str_kurz_abweichende_entfernung(self, entfernung=None):
        if entfernung is not None and self.entfernung != entfernung:
            title = "Die Entfernung weicht von der Entfernung der Adresse ab."
            return format_html(f"{self.str_kurz()}. "
                               f"<span title='{title}' style='color: red;'> ({self.entfernung} km)</span>")
        else:
            return f"{self.str_kurz()}"

    class Meta:
        db_table = 'adresse'
        verbose_name = "Adresse"
        verbose_name_plural = " Adressen"
        ordering = ['plz']


class Kunde(models.Model):
    id = models.AutoField(primary_key=True)
    anrede = models.CharField(max_length=20, blank=True, null=True)
    vorname = models.CharField(max_length=200, blank=True, null=True)
    nachname = models.CharField(max_length=200)
    adresse = models.ForeignKey(Adresse, blank=True, null=True, on_delete=models.SET_NULL)
    adresse_historisch = models.TextField(blank=True, null=True, verbose_name="Adresse Historie",
                                          help_text="Die ursprüngliche Adresse, falls die Adresse gelöscht wird.")

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

    def str_kurz_mit_anrede(self):
        anrede_prefix = f"{self.anrede} " if self.anrede else ""
        if self.vorname is not None:
            return f"{anrede_prefix}{self.vorname} {self.nachname}"
        else:
            return f"{anrede_prefix}{self.nachname}"

    class Meta:
        db_table = 'kunde'
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

    kunde_historisch = models.TextField(blank=True, null=True, verbose_name="Kunde Historie",
                                        help_text="Der ursprüngliche Kunde, falls der Kunde später gelöscht wird.")
    adresse_historisch = models.TextField(blank=True, null=True, verbose_name="Adresse Historie",
                                          help_text="Die ursprüngliche Adresse, falls die Adresse später gelöscht wird.")

    def __str__(self):
        return self.str_detaliert()

    def str_detaliert(self):
        fahrt_str = f"Datum: {self.datum.strftime('%d.%m.%Y')};"
        if self.kunde is not None:
            fahrt_str += f" Kunde: {self.kunde.str_kurz() if self.kunde else ''};"
        return fahrt_str + self.str_ziel()

    def str_ziel(self):
        ziel_str = ""
        if self.adresse is not None:
            ziel_str = f" Adresse: {self.adresse.str_kurz() if self.adresse else ''};"
        return ziel_str + f" Entfernung: {self.entfernung or '?'} km"

    def str_adresse_kurz(self):
        if self.adresse is not None:
            return
        return ""

    def str_entfernung(self):
        if self.adresse is not None:
            if self.adresse.entfernung != self.entfernung:
                title = "Die Entfernung weicht von der Entfernung der Adresse ab."
                return format_html(f"<span title='{title}' style='color: red;'>{self.entfernung or '?'}</span>")
            else:
                return str(self.entfernung)
        return str(self.entfernung)

    str_adresse_kurz.allow_tags = True

    class Meta:
        db_table = 'fahrt'
        verbose_name = "Fahrt"
        verbose_name_plural = "   Fahrten"
        ordering = ['-datum', '-id', 'kommentar']


class Einstellung(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    wert_date = models.DateField(null=True, blank=True)
    wert_char = models.CharField(max_length=255, null=True, blank=True)
    wert_decimal = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    wert_int = models.IntegerField(null=True, blank=True)
    beschreibung = models.TextField(max_length=1000, blank=True, null=True)

    def __str__(self):
        return self.name + ": " + str(self.wert)

    @property
    def wert(self):
        werte = list()
        if self.wert_date:
            werte.append(self.wert_date)
        if self.wert_char is not None:
            werte.append(self.wert_char)
        if self.wert_decimal:
            werte.append(self.wert_decimal)
        if self.wert_int:
            werte.append(self.wert_int)
        if len(werte) > 1:
            raise RuntimeError(
                f"Der Wert der Einstellung '{self.name}' ist nicht eindeutig, es darf nur ein Wert angegeben werden.")
        return werte[0] if len(werte) == 1 else None

    class Meta:
        db_table = 'einstellung'
        verbose_name = "Einstellung"
        verbose_name_plural = "Einstellungen"
        ordering = ['name']


@receiver(pre_delete, sender=Adresse)
def adresse_delete(sender, instance, **kwargs):
    """
    Beim Löschen der Adresse, wird die Adresse vorher als JSON Data am Kunden und an der Fahrt gespeichert,
    wo die Adresse referenziert wurde
    """
    kunden = Kunde.objects.filter(adresse=instance)
    for kunde in kunden:
        kunde.adresse_historisch = _get_model_historisch(instance)
        kunde.save()
    fahrten = Fahrt.objects.filter(adresse=instance)
    for fahrt in fahrten:
        fahrt.adresse_historisch = _get_model_historisch(instance)
        fahrt.save()


@receiver(pre_delete, sender=Kunde)
def kunde_delete(sender, instance, **kwargs):
    """
    Beim Löschen des Kunden, wird der Kunde vorher als JSON Data an der Fahrt gespeichert,
    wo der Kunde referenziert wurde
    """
    fahrten = Fahrt.objects.filter(kunde=instance)
    for fahrt in fahrten:
        fahrt.kunde_historisch = _get_model_historisch(instance)
        fahrt.save()


def _get_model_historisch(instance):
    data = serializers.serialize("json", [instance], indent=2)
    data = data.replace("~\n", "\\n")
    # strict=False wegen control character \n
    data_dict = json.loads(data, strict=False, encoding="utf-8")[0]
    data_dict["geloescht_am"] = datetime.datetime.now()
    return json.dumps(data_dict, indent=2, sort_keys=True, default=json_serial)
