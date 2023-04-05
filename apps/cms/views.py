from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.cms.models import CMS, TERMS_AND_COND, FAQ, ABOUT_US, CONTACT_US, PRIVACY_POLICIES
from apps.cms.serializers import CMSListSerializer, CMSCreateSerializer, CMSUpdateSerializer
from utils.exceptions import APIException404
from utils.response import response
from django.shortcuts import render


# Create your views here.


class CMSAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    """
    """
    def get(self, request, *args, **kwargs):
        qs = CMS.objects.all().values("id", "cms_type", "heading", "description")
        out_data = {"faq": [], "contact_us": {}, "about_us": {}, "privacy_policy": {}, "terms_and_cond": {}}
        for data in qs:
            if data["cms_type"] == FAQ:
                out_data["faq"].append(data)
            else:
                data.pop('heading')
                data.pop('id')
                if data["cms_type"] == ABOUT_US:
                    out_data["about_us"] = data
                elif data["cms_type"] == CONTACT_US:
                    out_data["contact_us"] = data
                elif data["cms_type"] == PRIVACY_POLICIES:
                    out_data["privacy_policy"] = data
                elif data["cms_type"] == TERMS_AND_COND:
                    out_data["terms_and_cond"] = data

        return response(status_code=200, data=out_data, message='success')

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = CMSCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response(status_code=200, message='Successfully created')

    def put(self, request, *args, **kwargs):
        data = request.data
        faq_obj = CMS.objects.filter(id=data.get("id"), cms_type=FAQ)
        if not faq_obj.exists():
            raise APIException404({"error": "Resource not found"})

        serializer = CMSUpdateSerializer(faq_obj.first(), data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response(status_code=200, message='Successfully updated')

    def delete(self, request, *args, **kwargs):
        qs = CMS.objects.filter(id=request.GET.get("id"), cms_type=FAQ)
        if not qs.exists():
            raise APIException404({"error": "Resource not found"})
        else:
            qs.delete()

        return response(status_code=200, message='Deleted Successfully ')


def StaticPagesForApplicationView(request):

    return render(request, "faq.html")

