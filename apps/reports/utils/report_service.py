import os
import xlsxwriter

from django.conf import settings
from django.db.models import F, Sum
from rest_framework.authtoken.admin import User

from apps.orders.models import Orders, COMPLETED, FAILED, PROCESSING, DU_PREPAID, ETISALAT, DU_POSTPAID, NOL_TOPUP, \
    HAFILAT, SALIK_DIRECT


class GenerateReportService:

    def __init__(self):
        xlsx_file_path = "{0}/reports/".format(
            settings.MEDIA_ROOT,
        )
        if not os.path.exists(xlsx_file_path):
            os.makedirs(xlsx_file_path)

    def xls_report(self, request, r_type):
        """
        Generate xlx report
        """
        if r_type == "1":
            # all the user
            report_data = User.objects.annotate(
                mobile=F('username'),
                country_code=F('user_profile__code'),
                is_otp_verified=F('user_profile__isotp_verified'),
                is_profile_complete=F('user_profile__is_profile_complete'),
                is_subadmin=F('user_profile__is_subadmin')
            ).values(
                "id", "first_name", "last_name", "email", "mobile", "country_code",
                "date_joined", "is_active", "is_otp_verified", "is_profile_complete", "is_subadmin")

            file_name = "total_users_report.xlsx"

        elif r_type == "2":
            # Active user
            report_data = User.objects.filter(is_active=True).annotate(
                mobile=F('username'),
                country_code=F('user_profile__code'),
                is_otp_verified=F('user_profile__isotp_verified'),
                is_profile_complete=F('user_profile__is_profile_complete'),
                is_subadmin=F('user_profile__is_subadmin')
            ).values(
                "id", "first_name", "last_name", "email", "mobile", "country_code",
                "date_joined", "is_active", "is_otp_verified", "is_profile_complete", "is_subadmin")

            file_name = "active_users_report.xlsx"

        elif r_type == "3":
            # Active user
            report_data = User.objects.filter(is_active=False).annotate(
                mobile=F('username'),
                country_code=F('user_profile__code'),
                is_otp_verified=F('user_profile__isotp_verified'),
                is_profile_complete=F('user_profile__is_profile_complete'),
                is_subadmin=F('user_profile__is_subadmin')
            ).values(
                "id", "first_name", "last_name", "email", "mobile", "country_code",
                "date_joined", "is_active", "is_otp_verified", "is_profile_complete", "is_subadmin")

            file_name = "in-active_users_report.xlsx"

        elif r_type in ("4", "6"):
            # total completed orders
            report_data = Orders.objects.filter(status=COMPLETED).values(
                "order_id", "user", "user__email", "service_type", "recharge_type", "recharge_number",
                                                                                    "amount", "status", "created_at")
            file_name = "completed_orders_report.xlsx"
            if r_type == "6":
                file_name = "order_revenue_report.xlsx"
                total_sum = Orders.objects.filter(status=COMPLETED).aggregate(sum=Sum('amount'))['sum']

        elif r_type == "5":
            # total completed orders
            report_data = Orders.objects.filter(status=FAILED).values(
                "order_id", "user", "user__email", "service_type", "recharge_number",
                "amount", "status", "created_at")
            file_name = "failed_orders_report.xlsx"

        if r_type in ("1", "2", "3"):
            report_col = ["user id", "first name", "last name", "email", "mobile number", "country code",
                          "date joined", "status", "profile complete status", "otp verified status", "sub admin"]
        else:
            report_col = ["order id", "user id", "use email", "order type", "recharge number",
                          "order status", "order date", "order amount"]

        xlsx_file_path = "{0}/reports/{1}".format(
            settings.MEDIA_ROOT,
            file_name
        )
        #print(report_data)
        workbook = xlsxwriter.Workbook(xlsx_file_path, options={'remove_timezone': True})
        worksheet = workbook.add_worksheet()
        worksheet.set_column(1, len(report_col), 25)

        # different formats required

        sample_header_format = workbook.add_format({'border': 2,
                                                    'bold': True, 'font_color': 'black', 'align': 'center',
                                                    'valign': 'vcenter'
                                                    })
        normal_value_format = workbook.add_format({'border': 1,
                                                   'bold': False, 'font_color': 'black', 'align': 'center',
                                                   'valign': 'vcenter', 'text_wrap': True,
                                                   })

        total_sum_format = workbook.add_format({'border': 1,
                                                'bold': True, 'font_color': 'black', 'align': 'center',
                                                'valign': 'vcenter', 'text_wrap': True,
                                                })

        date_format = workbook.add_format({'border': 1,
                                           'bold': False, 'font_color': 'black', 'align': 'center',
                                           'valign': 'vcenter', 'text_wrap': True,
                                           'num_format': 'yyyy-mm-dd hh:mm:ss'
                                           })

        # write address of customer in Excel
        for idx, col in enumerate(report_col):
            worksheet.write(0, idx, col.upper(), sample_header_format)

        for row, data in enumerate(report_data):
            worksheet.set_row(row, 25)
            if r_type in ("1", "2", "3"):
                worksheet.write(row + 1, 0, data.get("id"), normal_value_format)
                worksheet.write(row + 1, 1, data.get("first_name"), normal_value_format)
                worksheet.write(row + 1, 2, data.get("last_name"), normal_value_format)
                worksheet.write(row + 1, 3, data.get("email"), normal_value_format)
                worksheet.write(row + 1, 4, data.get("mobile"), normal_value_format)
                worksheet.write(row + 1, 5, data.get("country_code"), normal_value_format)
                worksheet.write(row + 1, 6, data.get("date_joined"), date_format)
                worksheet.write(row + 1, 7, data.get("is_active"), normal_value_format)
                worksheet.write(row + 1, 8, data.get("is_otp_verified"), normal_value_format)
                worksheet.write(row + 1, 9, data.get("is_profile_complete"), normal_value_format)
                worksheet.write(row + 1, 10, data.get("is_subadmin"), normal_value_format)
            else:
                worksheet.write(row + 1, 0, data.get("order_id"), normal_value_format)
                worksheet.write(row + 1, 1, data.get("user"), normal_value_format)
                worksheet.write(row + 1, 2, data.get("user__email"), normal_value_format)

                if data.get("service_type") == DU_PREPAID:
                    service_type = "DU PREPAID"
                elif data.get("service_type") == ETISALAT:
                    service_type = "ETISALAT"
                elif data.get("service_type") == DU_POSTPAID:
                    service_type = "DU POSTPAID"
                elif data.get("service_type") == NOL_TOPUP:
                    service_type = "NOL TOPUP"
                elif data.get("service_type") == HAFILAT:
                    service_type = "HAFILAT"
                elif data.get("service_type") == SALIK_DIRECT:
                    service_type = "SALIK DIRECT"

                worksheet.write(row + 1, 3, service_type, normal_value_format)
                worksheet.write(row + 1, 4, data.get("recharge_number"), normal_value_format)
                if data.get("status") == COMPLETED:
                    status = "COMPLETED"
                elif data.get("status") == PROCESSING:
                    status = "PROCESSING"
                elif data.get("status") == FAILED:
                    status = "FAILED"

                worksheet.write(row + 1, 5, status, normal_value_format)
                worksheet.write(row + 1, 6, data.get("created_at"), date_format)
                worksheet.write(row + 1, 7, data.get("amount"), normal_value_format)

            if r_type == "6":
                worksheet.write(row + 2, 7, "TOTAL AMOUNT = " + str(total_sum), total_sum_format)

        workbook.close()
        return {"url": request.build_absolute_uri("/media/" + xlsx_file_path.split('media/')[-1])}
