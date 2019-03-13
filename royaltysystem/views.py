from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.urls import reverse, reverse_lazy
from django.db import IntegrityError
from django.contrib import messages
from .utils.utils import kalkuler_akkumulert_when_utbetalt, kalkuler_fysisk_sum, kalkuler_total_akkumulert, Total_Row, get_active_periode_indices, kalkuler_digital_sum

import pdb;

from .models import Artist, Utgivelse, UtgivelseFormat, Periode

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
            if avregning_detaljert_list:
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
            if j == 0:
                messages.warning(request, 'Ingen data registrert på denne utgivelsen')
        art.utgivelser.append(ut)

    context = {
        'artist': art
    }

    return render(request, 'royaltysystem/artist.html', context)


def nyavregning_detaljert_digital(request, utgivelse):
    

def feil(request):
    return render(request, 'royaltysystem/test.html', {'name': 'Likt navn'})


def nyutgivelse(request, artist_id):
    if request.method == "POST":
        katalognr = request.POST['katalognr']
        navn = request.POST.get('utgivelse', False)
        dato = request.POST.get('dato', False)
        prosent = request.POST.get('prosent', False)
        digital = request.POST.get('digital', False)
        fysisk_format = request.POST.get('fysiskFormat', False)
        try:
            ut = Utgivelse(katalognr=katalognr, navn=navn, utgittdato=dato, artist=Artist.objects.get(pk=artist_id), royalty_prosent=prosent)
            ut.save()
            if digital:
                ut_dig = UtgivelseFormat(format="Digital", utgivelse=ut)
                ut_dig.save()
            if fysisk_format:
                ut_fys = UtgivelseFormat(format="Fysisk", fysisk_format_type=fysisk_format, utgivelse=ut)
                ut_fys.save()
        except IntegrityError:
            messages.error(request, IntegrityError.__cause__)
            return HttpResponseRedirect(reverse(artist, args=[artist_id]))
    return HttpResponseRedirect(reverse(utgivelse, args=[artist_id, katalognr]))


def utgivelse(request, artist_id, katalognr):
    periode = request.GET.get('periode', False)
    if not periode:
        ut = Utgivelse.objects.get(pk=katalognr)
        ut.perioder = []
        if ut.utgivelseformat_set.all():

            avregning_detaljert_list = ut.utgivelseformat_set.all()[0].avregning_detaljert_set.all()
            if avregning_detaljert_list:
                start, stop = get_active_periode_indices(avregning_detaljert_list)

                for _, l in enumerate(range(start, stop)):
                    ut.perioder.append(PERIODS[l].periode)
                
            else:
               ut.ingen_perioder = True
            context = {
                'utgivelse': ut,
                'artist_id': artist_id,
                'katalognr': katalognr
                }
            return render(request, "royaltysystem/velgperiode.html", context)
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
