from django.db.models import Q

from django.shortcuts import render
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics
from .serializers import UrlSerializer, SiteSerializer, EventSerializer

from event.models import Event, Url, Site


class BlockedDomains(generics.ListAPIView):
    """
    Este servicio entrega una lista de
    dominios(urls) que pertenesen a eventos de
    tipo bloqueo, o sea, dominios bloqueados.
    Nota. Todos los dominios bloqueados deberian
    pertenecer a un sitio.
    Ej. http://www.midominiobloqueado.com
    """

    permission_classes = (AllowAny,)

    queryset = Event.objects.filter(
        Q(type='bloqueo por DPI') |
        Q(type='bloqueo por DNS') |
        Q(type='bloqueo por IP')
    )
    serializer_class = UrlSerializer

    def get_queryset(self):
        url_list = self.queryset.values('target')
        queryset = Url.objects.filter(id__in=url_list)
        return queryset


class BlockedSites(BlockedDomains):
    """
    Este servicio entrega una lista de
    sitios que pertenesen a eventos de
    tipo bloqueo.
    O sea, sitios bloqueados.
    Ej. Mi Sitio Bloqueado
    """

    serializer_class = SiteSerializer

    def get_queryset(self):
        queryset = super(BlockedSites, self).get_queryset()

        site_list = queryset.values('site')
        queryset = Site.objects.filter(id__in=site_list)
        return queryset


class EventList(generics.ListAPIView):

    permission_classes = (AllowAny,)

    queryset = Event.objects.filter(draft=False)
    serializer_class = EventSerializer
