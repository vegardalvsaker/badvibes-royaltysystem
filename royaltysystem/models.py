from django.db import models
from django.utils import timezone

# Create your models here.
class Artist(models.Model):
    name = models.CharField(max_length=200)
    contract_since = models.DateField()
    def __str__(self):
        return self.name


class Utgivelse(models.Model):
    katalognr = models.CharField(primary_key=True, max_length=6,)
    navn = models.CharField(max_length=200)
    utgittdato = models.DateField(default=timezone.now)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    def __str__(self):
        return self.katalognr + " " + self.artist.__str__()+" - " + self.navn


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
        return self.utgivelseFormat.__str__() +" | " + self.periode +" | Kilde: "+ self.kilde

class Avregning(models.Model):
    periode = models.CharField(max_length=7)
    bruttoinntekt = models.DecimalField(max_digits=10, decimal_places=2)
    royalty_prosent = models.DecimalField(max_digits=5, decimal_places=2)
    utgivelse = models.ForeignKey(Utgivelse, on_delete=models.CASCADE)
