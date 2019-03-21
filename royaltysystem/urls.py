from django.urls import path 

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add_artist', views.add_artist, name='add_artist'),
    #path('feil', views.feil, name='feil'),
    path('artist/<int:artist_id>/', views.artist, name='artist'),
    path('json', views.json, name='json'),
    path('artist/<int:artist_id>/nyutgivelse/', views.nyutgivelse, name='nyutgivelse'),
    #path('artist/<int:artist_id>/utgivelse/<int:utgivelse_id>', views.utgivelse, name="utgivelse"),
    path('artist/<int:artist_id>/utgivelse/<katalognr>', views.utgivelse, name='utgivelse'),
    path('artist/<int:artist_id>/utgivelse/<katalognr>/nydetaljertavregning', views.nyavregning_detaljert_digital, name='ny_detaljert_avregning')
]
