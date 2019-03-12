from django.db import models
from django.utils import timezone

# Create your models here.
class Artist(models.Model):
    name = models.CharField(max_length=200, unique=True)
    contract_since = models.DateField()
    def __str__(self):
        return self.name


class Utgivelse(models.Model):
    katalognr = models.CharField(primary_key=True, max_length=6,)
    navn = models.CharField(max_length=200)
    utgittdato = models.DateField(default=timezone.now)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    royalty_prosent = models.DecimalField(max_digits=5, decimal_places=2)
    def __str__(self):
        return self.katalognr + " " + self.artist.__str__()+" - " + self.navn

class Periode(models.Model):
    periode = models.CharField(primary_key=True, max_length=7)
    periode_start = models.DateField()
    periode_slutt = models.DateField()

    def __str__(self):
        return self.periode

class UtgivelseFormat(models.Model):
    format = models.CharField(max_length=10)
    fysisk_format_type = models.CharField(blank=True, max_length=20)
    utgivelse = models.ForeignKey(Utgivelse, on_delete=models.CASCADE)

    def __str__(self):
        if self.fysisk_format_type:
            return self.utgivelse.__str__() + " "+ self.format + " ["+ self.fysisk_format_type+"]"

        return self.utgivelse.__str__() + " "+ self.format


class Avregning_Detaljert(models.Model):
    periode         = models.CharField(max_length=7)
    periode_new     = models.ForeignKey(Periode, on_delete=models.CASCADE, null=True)
    kilde           = models.CharField(max_length=20)
    antall          = models.IntegerField(null=True, blank=True)
    inntekter       = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    kostnader       = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    dl_utgivelse    = models.IntegerField(null=True, blank=True)
    dl_spor         = models.IntegerField(null=True, blank=True)
    streams         = models.IntegerField(null=True, blank=True)
    brutto          = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    utgivelseFormat = models.ForeignKey(UtgivelseFormat, on_delete=models.CASCADE)

    def __str__(self):
        return self.utgivelseFormat.__str__() +" | " + self.periode_new.__str__() +" | Kilde: "+ self.kilde


class Avregning(models.Model):
    periode = models.ForeignKey(Periode, on_delete=models.CASCADE)
    bruttoinntekt = models.DecimalField(max_digits=10, decimal_places=2)
    kostnader = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    utbetalt = models.BooleanField(default=False)
    utgivelse = models.ForeignKey(Utgivelse, on_delete=models.CASCADE)

    def __str__(self):
        return "Avregning for " + self.utgivelse.__str__() + " - " + self.periode.__str__()
