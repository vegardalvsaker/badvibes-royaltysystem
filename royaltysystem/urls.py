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
    path('artist/<int:artist_id>/utgivelse/<katalognr>/nydetaljertavregning', views.avregning_detaljert, name='avregning_detaljert'),
    path('artist/<int:artist_id>/utgivelse/<katalognr>/nydetaljertavregning/digital', views.add_avregning_detaljert_digital, name='add_avregning_detaljert_digital'),
    path('artist/<int:artist_id>/utgivelse/<katalognr>/nydetaljertavregning/fysisk', views.add_avregning_detaljert_fysisk, name='add_avregning_detaljert_fysisk')
]
