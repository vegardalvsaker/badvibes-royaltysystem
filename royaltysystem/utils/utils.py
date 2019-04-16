from ..models import Artist, Periode, Utgivelse, UtgivelseFormat, Avregning, Avregning_Detaljert
import pdb
PERIODS = Periode.objects.all()

def kalkuler_akkumulert_when_utbetalt(avregninger, attribute):
    if len(avregninger) > 0:
        return getattr(avregninger[len(avregninger)-1], attribute, False)
    else:
        return 0
        

def kalkuler_fysisk_sum(fysisk_liste):
    
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

    current_periode_index = get_current_periode(periode)

    brutto = 0
    streams = 0
    dl_spor = 0
    dl_utgivelse = 0
    fysisk_salg = 0

    first_periode, last_periode = get_active_periode_indices(digital_avregning_detaljert_list)

    ##Sjekker at perioden er innenfor utgivelsens første og siste periode.
    if current_periode_index >= first_periode and current_periode_index <= last_periode:
        for i in range(first_periode, current_periode_index):
            fysisk_liste = fysisk_format.avregning_detaljert_set.filter(periode_new=PERIODS[i].periode)
            fysisk_sum = kalkuler_fysisk_sum(fysisk_liste)
            brutto += fysisk_sum['brutto']
            fysisk_salg += fysisk_sum['antall']

        for j, a in enumerate(digital_avregning_detaljert_list):
            ##Uheldig sjekk. Forutsetter at dataen kommer sotert etter periode rekkefølge
            if a.periode_new.periode == PERIODS[current_periode_index].periode:
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

def kalkuler_total_akkumulert_digital(digital_list, periode):
    brutto = 0
    streams = 0
    dl_spor = 0
    dl_utgivelse = 0
    current_periode_index = get_current_periode(periode)
    first_periode, last_periode = get_active_periode_indices(digital_list)
    
    for j, a in enumerate(digital_list):
        ##Uheldig sjekk. Forutsetter at dataen kommer sotert etter periode rekkefølge
        if a.periode_new.periode == PERIODS[current_periode_index].periode:
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
    akkumulert_digital = Total_Digital_Row('Akkumulert', dl_utgivelse, dl_spor, streams, brutto)
    return akkumulert_digital

    return None

def kalkuler_total_akkumulert_fysisk(fysisk_list, periode):
    fysisk_salg = 0
    brutto = 0
    current_periode_index = get_current_periode(periode)
    first_periode, last_periode = get_active_periode_indices(fysisk_list)
    fysisk_list_thisperiod = []
    for av, i in enumerate(fysisk_list):
        if i.periode_new.periode == periode:
            fysisk_list_thisperiod.append(av)                 

    if current_periode_index >= first_periode and current_periode_index <= last_periode:
        for i in range(first_periode, current_periode_index):
            
            fysisk_sum = kalkuler_fysisk_sum(fysisk_list_thisperiod)
            brutto += fysisk_sum['brutto']
            fysisk_salg += fysisk_sum['antall']
        akkumulert_fysisk = Total_Fysisk_Row('Akkumulert', fysisk_salg, brutto)
        return akkumulert_fysisk
    
    return None

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
            if d.periode_new.periode == p.periode:
                active_period_indices.append(j)
    myset = set(active_period_indices)
    first_periode = myset.pop()
    if len(myset) == 0:
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

def get_prev_and_next_periode(periode):
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
    return forrige_periode, neste_periode

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

class Total_Fysisk_Row(object):
    avregning = ""
    fysisksalg = 0
    brutto = 0.00

    def __init__(self, avregning, fysisksalg, brutto):
        self.avregning = avregning
        self.fysisksalg = fysisksalg
        self.brutto = brutto

class Total_Digital_Row(object):
    avregning = ""
    DL_utgivelse = 0
    DL_spor = 0
    streams = 0
    brutto = 0.00

    def __init__(self, avregning, DL_utgivelse, DL_spor, streams, brutto):
        self.avregning = avregning
        self.DL_utgivelse = DL_utgivelse
        self.DL_spor = DL_spor
        self.streams = streams
        self.brutto = brutto
