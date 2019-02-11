from django.urls import path 

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('artist/<int:pk>/', views.ArtistView.as_view(), name='artist'),
    path('artist/<int:artist_id>/nyutgivelse/', views.nyutgivelse, name='nyutgivelse'),
    #path('artist/<int:artist_id>/utgivelse/<int:utgivelse_id>', views.utgivelse, name="utgivelse"),
    path('artist/<int:artist_id>/utgivelse/<katalognr>', views.utgivelse, name='utgivelse'),
]
