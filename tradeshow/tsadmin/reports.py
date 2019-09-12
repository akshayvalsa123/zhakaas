import os
import logging
import base64

from django.views.generic import View
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from django.http import HttpResponse

from api.models import Tradeshow
from api.models import ReportUrls
from api.models import ExhibitorBooth
from api.models import Lead
from tradeshow.common import model_apis as modelAPI
from tradeshow.common import error_codes as errorCodes
from tradeshow.common.utils import _buildResponse
from tradeshow.common.exceptions import ReportException


log = logging.getLogger(__name__)

class ExhibitorReportView(View):
    """
    """
    def dispatch(self, request, *args, **kwargs):
        return super(ExhibitorReportView, self).dispatch(request, *args, **kwargs)
    
    def get(self, request):
        """
        """
        log.info("ExhibitorReportView:get")
        try:            
            # Get the reportID and extract tradeshow/exhibitor information.
            reportID = request.GET.get('reportID')
            log.info("ExhibitorReportView:get, reportID:[%s]" % reportID)
            if not reportID:
                raise ReportException(errorCodes.REQUEST_PARAMETER_IS_REQUIRED, "reportID not provided")
            try:
                reportData = base64.b64decode(reportID)
                log.info("ExhibitorReportView:get, reportData: [%s]" % reportData)
                tradeshowName, exhibitorName, now = reportData.split('#')
            except:
                raise ReportException(errorCodes.INVALID_REPORTID, "Invalid reportID provided")
            # Get tradeshow and exhibitor instances
            log.info("ExhibitorReportView:get, tradeshowName:[%s], exhibitorName: [%s], now: [%s]" % (tradeshowName, exhibitorName, now))
            tradeshow = modelAPI.getTradeshowByName(tradeshowName)
            if not tradeshow:
                raise ReportException(errorCodes.TRADESHOW_NOT_EXISTS, "Tradeshow not exists")
            log.info("ExhibitorReportView:get, tradeshow: [%s]" % tradeshow)
            exhibitor = modelAPI.getExhibitorByName(exhibitorName)
            if not exhibitor:
                raise ReportException(errorCodes.EXHIBITOR_NOT_EXISTS, "Exhibitor not exists")
            log.info("ExhibitorReportView:get, exhibitor: [%s]" % exhibitor)
            # Get the report urls for the tradeshow
            reportUrls = ReportUrls.objects.filter(tradeshow=tradeshow).order_by('seq')
            if not reportUrls:
                raise ReportException(errorCodes.TRADESHOW_NO_REPORTS_CONFIGURED, "No reports available for the tradeshow.")
            log.info("ExhibitorReportView:get, reportUrls: [%s]" % reportUrls)
            # Build the reports information.
            reports = []
            server = settings.SERVER
            _tradeshowName = tradeshowName.replace(' ', '_')
            _exhibitorName = exhibitorName.replace(' ', '_')
            # Prepare base path where report snapshots are stored.
            baseResourcePath = "%s/static/%s/%s" % (server, _tradeshowName, _exhibitorName)            
            log.info("ExhibitorReportView:get, baseResourcePath: [%s]" % baseResourcePath)
            for reportUrl in reportUrls:
                reportName = reportUrl.name
                _reportName = reportName.replace(' ', '_')
                image = "%s/%s.png" % (baseResourcePath, _reportName)
                report = dict()
                report['name'] = reportName
                report['image'] = image
                reports.append(report)
            # Get the lead count
            exhibitorBooths = ExhibitorBooth.objects.filter(exhibitor=exhibitor)
            leadCount = Lead.objects.filter(exhibitorBooth__in = exhibitorBooths).count()
            reportInfo = {'tradeshow': tradeshow, 'exhibitor':exhibitor, 'reports': reports, 'leadCount':leadCount}
            log.info("ExhibitorReportView:get, reportInfo: [%s]" % reportInfo)
            return render_to_response("graph_report.html", reportInfo)
        except ReportException as ex:
            log.info("ExhibitorReportView:get, Exception, statusCode: [%s], Message: [%s]" % (ex.statusCode, ex.message))
            return HttpResponse(ex.message)
        except Exception as ex:
            statusCode = errorCodes.EXHIBITOR_REPORT_VIEW_EXCEPTION
            log.info("ExhibitorReportView:get, Exception:[%s]" % str(ex))
            return HttpResponse("Exception in getting report.")

class DownloadReportView(View):
    """
    """
    def dispatch(self, request, *args, **kwargs):
        return super(DownloadReportView, self).dispatch(request, *args, **kwargs)
    
    def get(self, request):
        """
        """
        try:        

            # Get the reportID and extract tradeshow/exhibitor information.
            reportID = request.GET.get('reportID')
            log.info("DownloadReportView:get, reportID:[%s]" % reportID)
            if not reportID:
                raise ReportException(errorCodes.REQUEST_PARAMETER_IS_REQUIRED, "reportID not provided")
            # Get the report format
            reportFormat = request.GET.get('format', '').strip()
            log.info("DownloadReportView:get, format:[%s]" % reportFormat)
            if not reportFormat:
                raise ReportException(errorCodes.REQUEST_PARAMETER_IS_REQUIRED, "format not provided")
            if reportFormat not in ['csv', 'pdf']:
                raise ReportException(errorCodes.INVALID_REPORT_FORMAT, "Invalid report format provided")
            try:
                reportData = base64.b64decode(reportID)
                log.info("DownloadReportView:get, reportData: [%s]" % reportData)
                tradeshowName, exhibitorName, now = reportData.split('#')
            except:
                raise ReportException(errorCodes.INVALID_REPORTID, "Invalid reportID provided")
            # Get tradeshow and exhibitor instances
            log.info("DownloadReportView:get, tradeshowName:[%s], exhibitorName: [%s], now: [%s]" % (tradeshowName, exhibitorName, now))
            tradeshow = modelAPI.getTradeshowByName(tradeshowName)
            if not tradeshow:
                raise ReportException(errorCodes.TRADESHOW_NOT_EXISTS, "Tradeshow not exists")
            log.info("DownloadReportView:get, tradeshow: [%s]" % tradeshow)
            exhibitor = modelAPI.getExhibitorByName(exhibitorName)
            if not exhibitor:
                raise ReportException(errorCodes.EXHIBITOR_NOT_EXISTS, "Exhibitor not exists")
            log.info("DownloadReportView:get, exhibitor: [%s]" % exhibitor)
            # Build the tradeshow and exhibitor report path
            reportPath = settings.TRADESHOW_REPORT_LOCATION
            _tradeshowName = tradeshowName.replace(' ', '_')
            tradeshowReportPath = reportPath + os.sep + _tradeshowName
            log.info("DownloadReportView:get, tradeshowReportPath: [%s]" % tradeshowReportPath)
            if not os.path.exists(tradeshowReportPath):
                raise ReportException(errorCodes.TRADESHOW_REPORT_PATH_NOT_EXISTS, "Tradeshow report path not exists")
            exhibitorReportPath = tradeshowReportPath + os.sep + exhibitorName.replace(' ', '_')
            log.info("DownloadReportView:get, exhibitorReportPath: [%s]" % exhibitorReportPath)
            if not os.path.exists(exhibitorReportPath):
                raise ReportException(errorCodes.EXHIBITOR_REPORT_PATH_NOT_EXISTS, "Exhibitor report path not exists")
            if reportFormat == "csv":
                csvFile = exhibitorReportPath + os.sep + exhibitorName + ".csv"
                log.info("DownloadReportView:get, csvFile: [%s]" % csvFile)
                if not os.path.exists(csvFile):
                    raise ReportException(errorCodes.EXHIBITOR_REPORT_CSV_FILE_NOT_EXISTS, "Exhibitor report CSV file not exists")
                fp = open(csvFile, "rb")
                data = fp.read()
                fp.close()
                response = HttpResponse(data, content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename=%s.csv' % exhibitorName
                return response
            elif reportFormat == "pdf":
                pdfFile = exhibitorReportPath + os.sep + exhibitorName + ".pdf"
                log.info("DownloadReportView:get, pdfFile: [%s]" % pdfFile)
                if not os.path.exists(pdfFile):
                    raise ReportException(errorCodes.EXHIBITOR_REPORT_PDF_FILE_NOT_EXISTS, "Exhibitor report PDF file not exists")
                fp = open(pdfFile, "rb")
                data = fp.read()
                fp.close()
                response = HttpResponse(data, content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename=%s.pdf' % exhibitorName
                return response
        except ReportException as ex:
            log.info("DownloadReportView:get, Exception, statusCode: [%s], message: [%s]" % (ex.statusCode, ex.message))
            return HttpResponse("Unable to download report.")
        except Exception as ex:
            statusCode = errorCodes.DOWNLOAD_REPORT_VIEW_EXCEPTION
            log.info("DownloadReportView:get, Exception:[%s]" % str(ex))
            return HttpResponse("Unable to download report.")
