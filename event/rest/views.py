from django.db.models import Q

from django.shortcuts import render
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics
from .serializers import UrlSerializer

from event.models import Event, Url


class BlockedDomains(generics.ListAPIView):

    permission_classes = (AllowAny,)

    queryset = Event.objects.filter(
        Q(type='bloqueo por DPI') |
        Q(type='bloqueo por DNS') |
        Q(type='bloqueo por IP')
    ).select_related('target')
    serializer_class = UrlSerializer

    def get_queryset(self):

        url_list = self.queryset.values('target')
        queryset = Url.objects.filter(id__in=url_list).distinct()
        return queryset


class BlockedSites(generics.ListAPIView):

    permission_classes = (AllowAny,)

    queryset = Event.objects.filter(
        Q(type='bloqueo por DPI') |
        Q(type='bloqueo por DNS') |
        Q(type='bloqueo por IP')
    ).select_related('target')
    serializer_class = UrlSerializer

    def get_queryset(self):

        url_list = self.queryset.values('target')
        queryset = Url.objects.filter(id__in=url_list).distinct()
        return queryset
