from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from serializers import (
    DetailEventCaseSerializer,
    CaseSerializer
)
from Case.models import Case


class DetailCaseRestView(generics.RetrieveAPIView):

    #authentication_classes = (TokenAuthentication, BasicAuthentication)
    #permission_classes = (IsAuthenticated,)
    permission_classes = (AllowAny,)
    queryset = Case.objects.filter(draft=False)
    lookup_url_kwarg = 'case_id'
    serializer_class = CaseSerializer


class DetailEventCaseRestView(generics.RetrieveAPIView):

    #authentication_classes = (TokenAuthentication, BasicAuthentication)
    #permission_classes = (IsAuthenticated,)
    permission_classes = (AllowAny,)
    queryset = Case.objects.filter(draft=False)
    lookup_url_kwarg = 'case_id'
    serializer_class = DetailEventCaseSerializer


class ListCaseView(generics.ListAPIView):

    #authentication_classes = (TokenAuthentication, BasicAuthentication)
    #permission_classes = (IsAuthenticated,)
    permission_classes = (AllowAny,)
    queryset = Case.objects.filter(draft=False)
    serializer_class = CaseSerializer