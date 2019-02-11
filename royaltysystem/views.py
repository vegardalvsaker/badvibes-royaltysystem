from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views import generic

from .models import Artist, Utgivelse


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
    fysisk = utgivelsen.utgivelseformat_set.filter(format__startswith='Fysisk')[0]
    digital = utgivelsen.utgivelseformat_set.filter(format__startswith='Digital')[0]

    fysisksum = kalkulerFysiskSum(fysisk, periode)
    context = {
        'periode': periode,
        'utgivelse': utgivelsen,
        'fysisk': {
            'data': fysisk,
            'sum': fysisksum
            },
        'digital': digital
    }
    return render(request, 'royaltysystem/utgivelse.html/', context)


def kalkulerFysiskSum(fysisk, periode):
    fysiskListe = fysisk.avregning_detaljert_set.filter(periode__startswith=periode)
    antall = sum(a.antall for a in fysiskListe)
    inntekter = sum(a.inntekter for a in fysiskListe)
    kostnader = sum(a.kostnader for a in fysiskListe)

    return {
        'antall': antall,
        'inntekter': inntekter,
        'kostnader': kostnader,
        'brutto': inntekter-kostnader
    }
    
