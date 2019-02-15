from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views import generic

from .models import Artist, Utgivelse

PERIODS = {
        0: 'P2 2016',
        1: 'P1 2017',
        2: 'P2 2017',
        3: 'P1 2018',
        4: 'P2 2018',
        5: 'P1 2019',
        6: 'P2 2019',
        7: 'P1 2020',
        8: 'P2 2020',
        9: 'P1 2020'
        }

class IndexView(generic.ListView):
    template_name = 'royaltysystem/index.html'
    context_object_name = 'artist_list'
   
    def get_queryset(self):
        """Return all Artists"""
        return Artist.objects.all()

class ArtistView(generic.DetailView):
    model = Artist
    template_name = 'royaltysystem/artist.html'

    """
    formdata = {}
    if request.POST:
        formdata = {
            'katalognr': request.POST['katalognr'],
            'navn': request.POST['navn'],
            'dato': request.POST['utgittdato']
        }

    art = get_object_or_404(Artist, pk=artist_id)    
    if formdata:
        context = {'formdata': formdata, 'artist': art}
    else:
        context = {'artist': art}
    return render(request, 'royaltysystem/artist.html', context)"""


def nyutgivelse(request, artist_id):
    katalognr = request.POST['katalognr']
    navn = request.POST['navn']
    dato = request.POST['utgittdato']
    return HttpResponse("Katalognr %s, Navn %s, dato utgitt %s" % (katalognr, navn, dato))

def utgivelse(request, artist_id, katalognr):
    periode = request.GET.get('periode', False)
    utgivelsen = get_object_or_404(Utgivelse, pk=katalognr)
    fysisk_format = utgivelsen.utgivelseformat_set.filter(format__startswith='Fysisk')[0]
    fysisk  = fysisk_format.avregning_detaljert_set.filter(periode__startswith=periode)
    digital = utgivelsen.utgivelseformat_set.filter(format__startswith='Digital')[0].avregning_detaljert_set.filter(periode__startswith=periode)

    total = kalkulerTotal(periode, utgivelsen)
    fysisk_sum = kalkulerFysiskSum(fysisk_format, periode)
    context = {
        'periode': periode,
        'perioder': PERIODS,
        'utgivelse': utgivelsen,
        'fysisk': {
            'data': fysisk,
            'sum': fysisk_sum
            },
        'digital': digital,
        'total': total
    }
    return render(request, 'royaltysystem/utgivelse.html/', context)


def kalkulerFysiskSum(fysisk, periode):
    fysisk_liste = fysisk.avregning_detaljert_set.filter(periode__startswith=periode)
    antall    = sum(a.antall for a in fysisk_liste)
    inntekter = sum(a.inntekter for a in fysisk_liste)
    kostnader = sum(a.kostnader for a in fysisk_liste)

    return {
        'antall': antall,
        'inntekter': inntekter,
        'kostnader': kostnader,
        'brutto': inntekter-kostnader
    }

##Finn index til periode. Summer all bruttoen til både fysisk og digital fra første periode, til og med til nåverende periode

def kalkulerTotal(periode, utgivelse):
    fysisk_format = utgivelse.utgivelseformat_set.filter(format__startswith='Fysisk')[0]
    digital_avregning_detaljert_list = utgivelse.utgivelseformat_set.filter(format__startswith='Digital')[0].avregning_detaljert_set.all()

    current_period_index = 0
    for k in PERIODS:
        if PERIODS[k] == periode:
            current_period_index = k

    brutto = 0

    for i in range(current_period_index+1):
        brutto += kalkulerFysiskSum(fysisk_format, PERIODS[i])['brutto']

    for j, a in enumerate(digital_avregning_detaljert_list):
        if a.periode == PERIODS[current_period_index+2]:
            break
        else:
            brutto += a.brutto

    akkumulert = Total_Row('Akkumulert',13, 1, 0, 8089, 1302.43)
    denne = Total_Row('Denne',3, 0, 0, 162, 251.83)
    totalt = Total_Row('Totalt',
        akkumulert.fysisksalg + denne.fysisksalg,
        akkumulert.DL_utgivelse + denne.DL_utgivelse,
        akkumulert.DL_spor + denne.DL_spor,
        akkumulert.streams + denne.streams,
        akkumulert.brutto + denne.brutto)
    total = [akkumulert, denne, totalt]    

    return total

class Total_Row(object):
    avregning = ""
    fysisksalg = 0
    DL_utgivelse = 0
    DL_spor = 0
    streams = 0
    brutto = 0.00

    def __init__(self, avregning, fysisksalg, DL_utgivelse, DL_spor, streams, brutto):
        self.avregning = avregning
        self.fysisksalg = fysisksalg
        self.DL_utgivelse = DL_utgivelse
        self.DL_spor = DL_spor
        self.streams = streams
        self.brutto = brutto