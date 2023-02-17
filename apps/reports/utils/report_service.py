import pdfkit
from django.conf import settings
from django.template.loader import render_to_string


class GenerateReportService:

    def pdf_report(self, customer_data, report_data, rp_no=1):
        """
        Generate pdf report
        """
        file_name = "report_{0}_{1}.pdf".format(report_data['id'], rp_no)
        pdf_file_path = "{0}reports/{1}".format(
            settings.MEDIA_ROOT,
            file_name
        )
        context = {
            "customer_data": customer_data,
        }
        options = {
            'page-size': 'A4',
            'dpi': 400,
            'zoom': '1.00',
            'margin-top': '0.115in',
            'margin-right': '0.115in',
            'margin-bottom': '0.115in',
            'margin-left': '0.115in',
        }

        html_body = render_to_string("pdf_report.html", {'data': context})
        # create pdf file
        pdfkit.from_string(html_body, pdf_file_path, options=options)
        return {
            "url": pdf_file_path.split('media/')[-1],
        }
