from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.reports.utils.report_service import GenerateReportService, ReportData
from utils.exceptions import APIException404, APIException400
from utils.response import response


class ReportAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        if not self.request.GET.get('report_type'):
            raise APIException400({
                "error": "Report type is required"
            })
        data = GenerateReportService().xls_report(request, self.request.GET.get('report_type'))
        return response(status_code=200, data=data, message='success')


class ReportDataAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        return response(
            status_code=200,
            data=ReportData().generate_data(),
            message='success')
