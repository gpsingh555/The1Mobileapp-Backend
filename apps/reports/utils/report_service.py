import pdfkit
import xlsxwriter
from django.conf import settings
from django.template.loader import render_to_string


class GenerateReportService:
    pass
    # def xls_report(self, data, ):
    #     """
    #     Generate xlx report
    #     """
    #     file_name = "report_{0}_{1}.xlsx".format(report_data['id'], rp_no)
    #     xlsx_file_path = "{0}reports/{1}".format(
    #         settings.MEDIA_ROOT,
    #         file_name
    #     )p
    #     workbook = xlsxwriter.Workbook(xlsx_file_path)
    #     worksheet = workbook.add_worksheet()
    #     worksheet.set_column(1, 4, 22)
    #
    #     # different formats required
    #     b_black_cell_format = workbook.add_format({'bold': True,
    #                                                'font_color': 'black'})
    #     data_cell_format = workbook.add_format({'align': 'left',
    #                                             'font_color': 'black', 'text_wrap': True,
    #                                             'num_format': 'mm/dd/yyyy'})
    #     sample_header_format = workbook.add_format({'border': 2,
    #                                                 'bold': True, 'font_color': 'black', 'align': 'center',
    #                                                 'valign': 'vcenter'
    #                                                 })
    #     sample_value_format = workbook.add_format({'border': 1,
    #                                                'bold': False, 'font_color': 'black', 'align': 'center',
    #                                                'valign': 'vcenter', 'text_wrap': True,
    #                                                })
    #
    #     # write address of customer in Excel
    #     worksheet.write(10, 0, 'To:', b_black_cell_format)
    #     # write report detail headings
    #     worksheet.write(10, 3, 'Report #', b_black_cell_format)
    #     worksheet.write(11, 3, 'Customer #', b_black_cell_format)
    #     worksheet.write(12, 3, 'Received Date', b_black_cell_format)
    #     worksheet.write(13, 3, 'Report Date', b_black_cell_format)
    #     worksheet.write(14, 3, 'Page', b_black_cell_format)
    #     worksheet.write(15, 3, 'P.O.#', b_black_cell_format)


