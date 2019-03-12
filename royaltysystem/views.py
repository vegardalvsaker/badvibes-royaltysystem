from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.urls import reverse, reverse_lazy
from django.db import IntegrityError
from django.contrib import messages

import pdb;

from .models import Artist, Utgivelse, Periode

PERIODS = Periode.objects.all()

def index(request):
    template_name = 'royaltysystem/index.html'
    artist_list = Artist.objects.all()
    context = {
        'artist_list': artist_list
    }
    return render(request, template_name, context)
    

def add_artist(request):
    ##pdb.set_trace()
    artist_navn = request.POST.get('artist', False)
    contract_signed = request.POST.get('dateSigned', False)
    try:
        a = Artist(name=artist_navn, contract_since=contract_signed)
        a.save()
    except IntegrityError:
        messages.error(request, "Artistnavnet finnes fra før av")
        return HttpResponseRedirect('/royaltysystem')
    return HttpResponseRedirect('/royaltysystem')
    

def artist(request, artist_id):
    art = get_object_or_404(Artist, pk=artist_id)    
    art.utgivelser = []
    for i, ut in enumerate(art.utgivelse_set.all()):
        ut.avregninger = []
        ut.totalt = {}
        ut.perioder = []
        if len(ut.utgivelseformat_set.all()) > 0: 
            avregning_detaljert_list = ut.utgivelseformat_set.all()[0].avregning_detaljert_set.all()
            start, stop = get_active_periode_indices(avregning_detaljert_list)

            for _, l in enumerate(range(start, stop)):
                ut.perioder.append(PERIODS[l].periode)

        for j, avregning in enumerate(ut.avregning_set.all()):
            nettoinntekt = round(avregning.bruttoinntekt - avregning.kostnader, 2)

            if j == 0 or ut.avregninger[j-1].utbetalt:
                if nettoinntekt < 0:
                    avregning.nettoinntekt = nettoinntekt
                    avregning.labelcut = nettoinntekt
                    avregning.nettoinntekt_akkumulert = nettoinntekt
                else:
                    avregning.nettoinntekt = round(nettoinntekt * (ut.royalty_prosent / 100), 2)
                    avregning.nettoinntekt_akkumulert   = avregning.nettoinntekt
                    avregning.labelcut = avregning.bruttoinntekt - avregning.nettoinntekt

                avregning.bruttoinntekt_akkumulert  = avregning.bruttoinntekt
                avregning.kostnader_akkumulert      = avregning.kostnader
            else:
                avregning.bruttoinntekt_akkumulert  = avregning.bruttoinntekt + ut.avregninger[j-1].bruttoinntekt_akkumulert
                avregning.kostnader_akkumulert      = avregning.kostnader + ut.avregninger[j-1].kostnader_akkumulert
                if (ut.avregninger[j-1].nettoinntekt_akkumulert + nettoinntekt) < 0:
                    avregning.nettoinntekt  = nettoinntekt
                    avregning.labelcut      = nettoinntekt
                else:
                    avregning.nettoinntekt  = round(nettoinntekt * (ut.royalty_prosent / 100), 2) 
                    avregning.labelcut      = avregning.bruttoinntekt - avregning.nettoinntekt
                avregning.nettoinntekt_akkumulert   = round(avregning.nettoinntekt + ut.avregninger[j-1].nettoinntekt_akkumulert, 2)



            ##Kalkulerer totalt-raden
            ut.avregninger.append(avregning)
            ut.totalt['bruttoinntekt']              = sum(filter(None, (a.bruttoinntekt for a in ut.avregninger)))
            ut.totalt['bruttoinntekt_akkumulert']   = kalkuler_akkumulert_when_utbetalt(ut.avregninger, 'bruttoinntekt_akkumulert')
            ut.totalt['kostnader']                  = sum(filter(None, (a.kostnader for a in ut.avregninger)))
            ut.totalt['kostnader_akkumulert']       = kalkuler_akkumulert_when_utbetalt(ut.avregninger, 'kostnader_akkumulert')
            ut.totalt['nettoinntekt']               = sum(filter(None,(a.nettoinntekt for a in ut.avregninger)))
            ut.totalt['nettoinntekt_akkumulert']    = kalkuler_akkumulert_when_utbetalt(ut.avregninger, 'nettoinntekt_akkumulert')
            ut.totalt['labelcut']                   = sum(filter(None, (a.labelcut for a in ut.avregninger)))
        art.utgivelser.append(ut)

    context = {
        'artist': art
    }

    return render(request, 'royaltysystem/artist.html', context)

def kalkuler_akkumulert_when_utbetalt(avregninger, attribute):
    value = 0
    for i, a in enumerate(avregninger):
        if i == 0:
            value = getattr(a, attribute, False)
        elif avregninger[i-1].utbetalt:
            value = getattr(a, attribute, False)
        else:
            value += getattr(a, attribute, False)
    return value

def feil(request):
    return render(request, 'royaltysystem/test.html', {'name': 'Likt navn'})

def nyutgivelse(request, artist_id):
    """
    katalognr = request.POST['katalognr']
    navn = request.POST['navn']
    dato = request.POST['utgittdato']
    return HttpResponse("Katalognr %s, Navn %s, dato utgitt %s" % (katalognr, navn, dato))
    """
    return HttpResponseRedirect(reverse(artist, args=[artist_id]))

def utgivelse(request, artist_id, katalognr):
    periode = request.GET.get('periode', False)
    periode.replace("%20", " ")
    utgivelsen = get_object_or_404(Utgivelse, pk=katalognr)
    fysisk_format = utgivelsen.utgivelseformat_set.filter(format__startswith='Fysisk')[0]
    fysisk  = fysisk_format.avregning_detaljert_set.filter(periode__startswith=periode)
    digital = utgivelsen.utgivelseformat_set.filter(format__startswith='Digital')[0].avregning_detaljert_set.filter(periode__startswith=periode)

    fysisk_sum = kalkuler_fysisk_sum(fysisk_format, periode)
    digital_sum = kalkuler_digital_sum(digital)

    total_akkumulert = kalkuler_total_akkumulert(periode, utgivelsen)

    total_denne = Total_Row('Denne', fysisk_sum['antall'],
                            digital_sum['dl_utgivelse'], digital_sum['dl_spor'],
                            digital_sum['streams'],
                            fysisk_sum['brutto'] + digital_sum['brutto'])

    total_totalt = Total_Row('Totalt',
                             total_akkumulert.fysisksalg + total_denne.fysisksalg,
                             total_akkumulert.DL_utgivelse + total_denne.DL_utgivelse,
                             total_akkumulert.DL_spor + total_denne.DL_spor,
                             total_akkumulert.streams + total_denne.streams,
                             total_akkumulert.brutto + total_denne.brutto)
    total = [total_akkumulert, total_denne, total_totalt]


    current_periode_index = None
    for i, p in enumerate(PERIODS):
        if p.periode == periode:
            current_periode_index = i

    if current_periode_index is 0:
        forrige_periode = PERIODS[0].periode
        neste_periode = PERIODS[1].periode
    elif current_periode_index is (len(PERIODS)-1):
        forrige_periode = PERIODS[current_periode_index-1].periode
        neste_periode = PERIODS[current_periode_index].periode
    else:
        forrige_periode = PERIODS[current_periode_index-1].periode
        neste_periode = PERIODS[current_periode_index+1].periode
    
    context = {
        'artist_id': artist_id,
        'periode': periode,
        'forrige_periode': forrige_periode,
        'neste_periode': neste_periode,
        'utgivelse': utgivelsen,
        'fysisk': {
            'data': fysisk,
            'sum': fysisk_sum
            },
        'digital': {
            'data': digital,
            'sum': digital_sum
            },
        'total': total
    }
    return render(request, 'royaltysystem/utgivelse.html/', context)


def kalkuler_fysisk_sum(fysisk, periode):
    fysisk_liste = fysisk.avregning_detaljert_set.filter(periode__startswith=periode)

    antall    = sum(filter(None, (a.antall for a in fysisk_liste)))
    inntekter = sum(filter(None, (a.inntekter for a in fysisk_liste)))

    kostnader = sum(filter(None, (a.kostnader for a in fysisk_liste)))

    return {
        'antall': antall,
        'inntekter': inntekter,
        'kostnader': kostnader,
        'brutto': inntekter-kostnader
    }

##Finn index til periode. Summer all bruttoen til både fysisk og digital fra første periode,
#  til og med til nåverende periode

def kalkuler_total_akkumulert(periode, utgivelse):
    fysisk_format = utgivelse.utgivelseformat_set.filter(format__startswith='Fysisk')[0]
    digital_avregning_detaljert_list = utgivelse.utgivelseformat_set.filter(format__startswith='Digital')[0].avregning_detaljert_set.all()

    current_periode_index = 0
    for i, k in enumerate(PERIODS):
        if k.periode == periode:
            current_periode_index = i

    brutto = 0
    streams = 0
    dl_spor = 0
    dl_utgivelse = 0
    fysisk_salg = 0
    
    first_periode, last_periode = get_active_periode_indices(digital_avregning_detaljert_list)



    ##pdb.set_trace()
    ##Sjekker at perioden er innenfor utgivelsens første og siste periode.
    if current_periode_index >= first_periode and current_periode_index <= last_periode:
        for i in range(first_periode, current_periode_index):
            
            fysisk_sum = kalkuler_fysisk_sum(fysisk_format, PERIODS[i].periode)
            brutto += fysisk_sum['brutto']
            fysisk_salg += fysisk_sum['antall']

        for j, a in enumerate(digital_avregning_detaljert_list):
            if a.periode == PERIODS[current_periode_index].periode:
                break
            else:
                if a.brutto is not None:
                    brutto += a.brutto
                if a.dl_spor is not None:
                    dl_spor += a.dl_spor
                if a.dl_utgivelse is not None:
                    dl_utgivelse += a.dl_utgivelse
                if a.streams is not None:
                    streams += a.streams

    akkumulert = Total_Row('Akkumulert', fysisk_salg, dl_utgivelse, dl_spor, streams, brutto)
    return akkumulert

def kalkuler_digital_sum(digital_liste):
    DL_utgivelse = sum(filter(None, (d.dl_utgivelse for d in digital_liste)))
    DL_spor = sum(filter(None, (d.dl_spor for d in digital_liste)))
    streams = sum(filter(None, (d.streams for d in digital_liste)))
    brutto = sum(filter(None, (d.brutto for d in digital_liste)))

    digital_sum = {
        'kilde': 'Sum',
        'dl_utgivelse': DL_utgivelse,
        'dl_spor': DL_spor,
        'streams': streams,
        'brutto': brutto
    }

    return digital_sum

def get_active_periode_indices(avregning_detaljert_list):
    """
    Finds the index of the first and last period of the utgivelse

    Parameters:
    avregning_detaljert_list (list): List of avregning_detaljert-objects

    Returns:
    int: Index of first period, index of last period
    """
    active_period_indices = []
    for _, d in enumerate(avregning_detaljert_list):
        for j, p in enumerate(PERIODS):
            if d.periode == p.periode:
                active_period_indices.append(j)
    myset = set(active_period_indices)
    first_periode = myset.pop()
    last_periode = max(myset)
    return first_periode, last_periode

def get_current_periode(periode):
    current_periode_index = None
    for i, k in enumerate(PERIODS):
        if k.periode == periode:
            current_periode_index = i
    return current_periode_index

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
