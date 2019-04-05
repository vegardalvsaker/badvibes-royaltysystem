from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.urls import reverse, reverse_lazy
from django.db import IntegrityError
from django.contrib import messages
from .utils.utils import kalkuler_akkumulert_when_utbetalt, kalkuler_fysisk_sum, kalkuler_total_akkumulert, kalkuler_total_akkumulert_digital, kalkuler_total_akkumulert_fysisk, Total_Row,Total_Digital_Row, Total_Fysisk_Row, get_active_periode_indices, kalkuler_digital_sum, get_prev_and_next_periode

import pdb

from .models import Artist, Utgivelse, UtgivelseFormat, Periode, Avregning_Detaljert

PERIODS = Periode.objects.all()

def index(request):
    template_name = 'royaltysystem/index.html'
    artist_list = Artist.objects.all()
    for i, a in enumerate(artist_list):
        a.utgivelser = len(Utgivelse.objects.filter(artist=a))
    context = {
        'artist_list': artist_list
    }
    return render(request, template_name, context)

def json(request):
    return JsonResponse({'foo': 'bar'})

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
    art.sum = {  'akkumulert': {
                                    'brutto': 0,
                                    'kostnader': 0,
                                    'nettoinntekt': 0 
                                    },
                    'totalt': {     'brutto': 0,
                                    'kostnader': 0,
                                    'nettoinntekt': 0,
                                    'labelcut': 0
                    }
                }
    
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

            ut.avregninger.append(avregning)
        ##Kalkulerer totalt-raden
        ut.totalt['bruttoinntekt']              = sum(filter(None, (a.bruttoinntekt for a in ut.avregninger)))
        ut.totalt['bruttoinntekt_akkumulert']   = kalkuler_akkumulert_when_utbetalt(ut.avregninger, 'bruttoinntekt_akkumulert')
        ut.totalt['kostnader']                  = sum(filter(None, (a.kostnader for a in ut.avregninger)))
        ut.totalt['kostnader_akkumulert']       = kalkuler_akkumulert_when_utbetalt(ut.avregninger, 'kostnader_akkumulert')
        ut.totalt['nettoinntekt']               = sum(filter(None,(a.nettoinntekt for a in ut.avregninger)))
        ut.totalt['nettoinntekt_akkumulert']    = kalkuler_akkumulert_when_utbetalt(ut.avregninger, 'nettoinntekt_akkumulert')
        ut.totalt['labelcut']                   = sum(filter(None, (a.labelcut for a in ut.avregninger)))
       
        art.sum['totalt']['brutto'] += ut.totalt['bruttoinntekt']
        art.sum['akkumulert']['brutto'] += ut.totalt['bruttoinntekt_akkumulert']

        art.sum['totalt']['kostnader'] += ut.totalt['kostnader']
        art.sum['akkumulert']['kostnader'] += ut.totalt['kostnader_akkumulert']

        art.sum['totalt']['nettoinntekt'] += ut.totalt['nettoinntekt']
        art.sum['akkumulert']['nettoinntekt'] += ut.totalt['nettoinntekt_akkumulert']

        art.sum['totalt']['labelcut'] += ut.totalt['labelcut']
            
        art.utgivelser.append(ut)
    
    context = {
        'artist': art
    }

    return render(request, 'royaltysystem/artist.html', context)

def avregning_detaljert(request, artist_id, katalognr):
    
    digital = True
    fysisk = True

    try:
        UtgivelseFormat.objects.get(utgivelse=katalognr, format="Fysisk")
    except UtgivelseFormat.DoesNotExist:
        fysisk = False

    context = {
        'digital': digital,
        'fysisk': fysisk,
        'artist_id': artist_id,
        'katalognr': katalognr
    }
    return render(request, 'royaltysystem/avregning_detaljert_form.html', context)

def add_avregning_detaljert_digital(request, artist_id, katalognr):
    p = request.POST.get('periode')
    periode = Periode.objects.get_or_create(periode=p)[0]
    rader = int(request.POST.get('rader'))
    utgivelse_format = UtgivelseFormat.objects.get(utgivelse=katalognr, format='Digital')
    
    for i in range (1, rader+1):
        kilde = request.POST.get('kilde' + str(i))
        dl_utgivelse = request.POST.get('DLutgivelse' + str(i), False)
        dl_spor = request.POST.get('DLspor' + str(i), False)
        streams = request.POST.get('streams' + str(i), False)
        brutto = request.POST.get('brutto' + str(i), False)

        avreg_detalj = Avregning_Detaljert(periode_new=periode, kilde=kilde, dl_utgivelse=dl_utgivelse, dl_spor=dl_spor, streams=streams, brutto=brutto, utgivelseFormat=utgivelse_format)
        avreg_detalj.save()
    
    return HttpResponseRedirect(reverse(utgivelse, args=[artist_id, katalognr]))

def add_avregning_detaljert_fysisk(request, artist_id, katalognr):
    p = request.POST.get('periode')
    periode = Periode.objects.get_or_create(periode=p)[0]
    rader = int(request.POST.get('rader'))
    utgivelse_format = UtgivelseFormat.objects.get(utgivelse=katalognr, format='Fysisk')
    
    for i in range (1, rader+1):
        kilde = request.POST.get('kilde' + str(i))
        antall = request.POST.get('antall' + str(i), False)
        inntekter = request.POST.get('inntekter' + str(i), False)
        kostnader = request.POST.get('kostnader' + str(i), False)
        brutto = request.POST.get('brutto' + str(i), False)

        avreg_detalj = Avregning_Detaljert(periode_new=periode, kilde=kilde, antall=antall, inntekter=inntekter, kostnader=kostnader, brutto=brutto, utgivelseFormat=utgivelse_format)
        avreg_detalj.save()
    
    return HttpResponseRedirect(reverse(utgivelse, args=[artist_id, katalognr]))

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

def add_utgivelse_format(request, artist_id, katalognr):
    if request.method == "POST":
        digital = request.POST.get('digital', False)
        fysisk_format = request.POST.get('fysiskFormat', False)

        ut = Utgivelse.objects.get(pk=katalognr)
        try:
            if digital:
                ut_dig = UtgivelseFormat(format="Digital", utgivelse=ut)
                ut_dig.save()
            if fysisk_format:
                ut_fys = UtgivelseFormat(format="Fysisk", fysisk_format_type=fysisk_format, utgivelse=ut)
                ut_fys.save()
            return HttpResponseRedirect(reverse(avregning_detaljert, args=[artist_id, katalognr]))
        except IntegrityError:
            messages.error(request, IntegrityError.__cause__)
            return HttpResponseRedirect(reverse(artist, args=[artist_id]))
    return HttpResponseRedirect(reverse(artist, args=[artist_id]))
    
def utgivelse(request, artist_id, katalognr):
    periode = request.GET.get('periode', False)
    if not periode:
        ut = Utgivelse.objects.get(pk=katalognr)
        ut.perioder = []
        if ut.utgivelseformat_set.all():

            avregning_detaljert_list = ut.utgivelseformat_set.all()[0].avregning_detaljert_set.all()
            if len(avregning_detaljert_list) > 0:
                start, stop = get_active_periode_indices(avregning_detaljert_list)

                for _, l in enumerate(range(start, stop + 1)):
                    ut.ingen_perioder = False
                    ut.perioder.append(PERIODS[l].periode)
                ut.ingen_perioder = False
            else:
               ut.ingen_perioder = True
            context = {
                'utgivelse': ut,
                'artist_id': artist_id,
                'katalognr': katalognr
                }

            return render(request, "royaltysystem/velgperiode.html", context)
        else:
            return render(request, "royaltysystem/addformat.html", {'artist_id': artist_id, 'utgivelse': ut})
    periode.replace("%20", " ")
    utgivelsen = get_object_or_404(Utgivelse, pk=katalognr)

    forrige_periode, neste_periode = get_prev_and_next_periode(periode)

    context = {
        'artist_id': artist_id,
        'periode': periode,
        'forrige_periode': forrige_periode,
        'neste_periode': neste_periode,
        'utgivelse': utgivelsen,
    }

    formats = utgivelsen.utgivelseformat_set.all()
    
    if len(formats) is 1:
        if len(formats[0].avregning_detaljert_set.filter(periode_new=periode)) == 0:
            messages.warning(request, 'Ingen data registrert for ' + utgivelsen.__str__() + ' i perioden ' + periode)
            return HttpResponseRedirect(reverse(artist, args=[artist_id]))
        if formats[0].format == 'Fysisk':
            fysisk = formats[0].avregning_detaljert_set.filter(periode_new=get_periode(periode))
            fysisk_sum = kalkuler_fysisk_sum(fysisk)
            total = get_total_fysisk(formats[0], periode)

            context['format'] = formats[0].fysisk_format_type
            context['fysisk'] = {'data': fysisk, 'sum': fysisk_sum}
            context['total'] = total
            return render(request, "royaltysystem/utgivelse_fysisk.html", context)
        elif formats[0].format == 'Digital':
            digital = formats[0].avregning_detaljert_set.filter(periode_new=get_periode(periode))
            digital_sum = kalkuler_digital_sum(digital)
            total = get_total_digital(formats[0], periode)

            context['digital'] = {'data': digital, 'sum': digital_sum}
            context['total'] = total
            return render(request, "royaltysystem/utgivelse_digital.html", context)
        else:
            return render(request, "royaltysystem/feil.html", {})
    elif len(formats) is 2:

        fysisk_format = utgivelsen.utgivelseformat_set.filter(format__startswith='Fysisk')[0]
        fysisk  = fysisk_format.avregning_detaljert_set.filter(periode_new=get_periode(periode))
        digital = utgivelsen.utgivelseformat_set.filter(format__startswith='Digital')[0].avregning_detaljert_set.filter(periode_new=get_periode(periode))

        fysisk_sum = kalkuler_fysisk_sum(fysisk)
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

        context['fysisk'] = {'data': fysisk, 'sum': fysisk_sum}

        context['digital'] = {'data': digital, 'sum': digital_sum}

        context['total'] = total
        return render(request, 'royaltysystem/utgivelse.html/', context)
    return render(request, "royaltysystem/utgivelse_feil.html", {})

def get_total_fysisk(fysisk_format, periode):
    fysisk_whole_list = fysisk_format.avregning_detaljert_set.all()
    fysisk_thisperiod_list = fysisk_format.avregning_detaljert_set.filter(periode_new=periode)

    fysisk_sum = kalkuler_fysisk_sum(fysisk_thisperiod_list)

    total_akkumulert = kalkuler_total_akkumulert_fysisk(fysisk_whole_list, periode)

    total_denne = Total_Fysisk_Row('Denne', fysisk_sum['antall'], fysisk_sum['brutto'])

    total_totalt = Total_Fysisk_Row('Totalt', total_akkumulert.fysisksalg + total_denne.fysisksalg, total_akkumulert.brutto + total_denne.brutto)

    total = [total_akkumulert, total_denne, total_totalt]
    return total
    
def get_total_digital(digital_format, periode):
    digital_whole_list = digital_format.avregning_detaljert_set.all()
    digital_thisperiod_list = digital_format.avregning_detaljert_set.filter(periode_new=periode)

    digital_sum = kalkuler_digital_sum(digital_thisperiod_list)

    total_akkumulert = kalkuler_total_akkumulert_digital(digital_whole_list, periode)
    
    total_denne = Total_Digital_Row('Denne', digital_sum['dl_utgivelse'],
                                    digital_sum['dl_spor'], digital_sum['streams'],
                                        digital_sum['brutto'])

    total_totalt = Total_Digital_Row('Totalt',
                            total_akkumulert.DL_utgivelse + total_denne.DL_utgivelse,
                            total_akkumulert.DL_spor + total_denne.DL_spor,
                            total_akkumulert.streams + total_denne.streams,
                            total_akkumulert.brutto + total_denne.brutto)
    total = [total_akkumulert, total_denne, total_totalt]
    return total

def get_periode(periode):
    return Periode.objects.get(periode=periode)

def contains_periode(avregning_detaljert_list, periode):
    contains = False
    for i, a in enumerate(avregning_detaljert_list):
        if a.periode_new.__str__() == periode:
            contains = True
    return contains
