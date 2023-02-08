from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from account.models import country, city
from apps.sub_admin.serializers import CountrySerializer, CitySerializer, CountryDetailSerializer
from utils.response import response


class CountryViewSet(viewsets.ModelViewSet):
    queryset = country.objects.all()
    permission_classes = (IsAuthenticated,)
    ordering = ('name',)

    def get_serializer_class(self):
        if self.action == 'list':
            return CountrySerializer
        elif self.action == 'retrieve':
            return CountryDetailSerializer
        elif self.action == 'update':
            return CountrySerializer

        return super(CountryViewSet, self).get_serializer_class()

    def list(self, request, *args, **kwargs):
        response_data = super(CountryViewSet, self).list(request, *args, **kwargs)
        return response(data=response_data.data, message="success")

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer_class()
        data = serializer(instance).data
        return response(data=data, message="success")


class CityViewSet(viewsets.ModelViewSet):
    queryset = city.objects.all()
    serializer_class = CitySerializer
    permission_classes = (IsAuthenticated,)
    ordering = ('name',)

    def list(self, request, *args, **kwargs):
        response_data = super(CityViewSet, self).list(request, *args, **kwargs)
        return response(data=response_data.data, message="success")
