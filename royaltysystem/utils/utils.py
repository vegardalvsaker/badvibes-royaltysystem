from ..models import Artist, Periode, Utgivelse, UtgivelseFormat, Avregning, Avregning_Detaljert

PERIODS = Periode.objects.all()

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

def kalkuler_total_akkumulert(periode, utgivelse):
    """
    Finn index til periode. Summer all bruttoen til både fysisk og digital fra første periode,
    til og med til nåværende periode
    """

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
    if len(avregning_detaljert_list) == 1:
        last_periode = first_periode
    else:
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
