from django.contrib import admin

from .models import Artist, Utgivelse, UtgivelseFormat, Avregning, Avregning_Detaljert, Periode, Utbetaling
admin.site.register(Artist)
admin.site.register(Utgivelse)
admin.site.register(UtgivelseFormat)
admin.site.register(Avregning)
admin.site.register(Avregning_Detaljert)
admin.site.register(Periode)
admin.site.register(Utbetaling)
# Register your models here.
