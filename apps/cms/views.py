from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.cms.models import CMS
from apps.cms.serializers import CMSListSerializer, CMSCreateSerializer, CMSUpdateSerializer
from utils.exceptions import APIException404
from utils.response import response


# Create your views here.


class CMSAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    """
    """
    def get(self, request, *args, **kwargs):
        qs = CMS.objects.all()
        cms_data = CMSListSerializer(qs, many=True).data
        return response(status_code=200, data=cms_data, message='success')

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = CMSCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response(status_code=200, message='Successfully created')

    def put(self, request, *args, **kwargs):
        data = request.data
        cms_obj = CMS.objects.filter(id=data.get("id"))
        if not cms_obj.exists():
            raise APIException404({"error": "resource not found"})

        serializer = CMSUpdateSerializer(cms_obj, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response(status_code=200, message='Successfully updated')

    def delete(self, request, *args, **kwargs):
        qs = CMS.objects.filter(id=request.GET.get("id"))
        if not qs.exists():
            raise APIException404({"error": "resource not found"})
        else:
            qs.delete()

        return response(status_code=200, message='Successfully deleted')
