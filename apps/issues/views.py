from django.shortcuts import render
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from apps.issues.models import UserQuery
from apps.issues.serializers import QueryCreateSerializer, QueryListSerializer, QueryUpdateSerializer, \
    QueryPartialListSerializer
from utils.response import response


# Create your views here.

class QueryViewSet(viewsets.ModelViewSet):
    queryset = UserQuery.objects.all()
    serializer_class = QueryListSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (filters.OrderingFilter,)
    ordering = ('-created_at',)

    def get_serializer_class(self):
        if self.action == 'create':
            return QueryCreateSerializer
        elif self.action == 'update':
            return QueryUpdateSerializer

        return super(QueryViewSet, self).get_serializer_class()

    def list(self, request, *args, **kwargs):
        qs = UserQuery.objects.filter(user=request.user)
        response_data = self.serializer_class(qs, many=True).data
        return response(data=response_data, message="success")

    def retrieve(self, request, *args, **kwargs):
        response_data = super(QueryViewSet, self).retrieve(request, *args, **kwargs).data
        response_data["user"] = request.user.first_name + " " + request.user.last_name
        response_data["email"] = request.user.email
        response_data["mobile_number"] = request.user.username
        return response(data=response_data, message="success")

    def update(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()

        serializer = self.serializer_class(instance=instance,
                                           data=request.data,
                                           partial=True)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response(message="Updated Successfully", status_code=200)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,  # or request.data
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response(message="successfully created", status_code=201)

    @action(detail=False, methods=['GET'])
    def all(self, request, *args, **kwargs):
        """
        """
        qs = UserQuery.objects.all()
        response_data = QueryPartialListSerializer(qs, many=True).data
        return response(data=response_data, message="success")
