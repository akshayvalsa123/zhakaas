import time
import os
import logging
import base64
from datetime import datetime

from django.views.generic import View
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings

from api.models import Tradeshow
from api.models import ReportUrls
from tradeshow.common import model_apis as modelAPI
from tradeshow.common import error_codes as errorCodes
from tradeshow.common.utils import _buildResponse
from tradeshow.common.exceptions import ReportException

log = logging.getLogger(__name__)

class TradeshowReportView(View):
    """
    """
    def dispatch(self, request, *args, **kwargs):
        return super(TradeshowReportView, self).dispatch(request, *args, **kwargs)
    
    def get(self, request):
        """
        """
        log.info("TradeshowReportView:get")
        tradeshows = Tradeshow.objects.all()
        return render_to_response('report_view.html', {'tradeshows': tradeshows}, context_instance = RequestContext(request))

    def post(self, request):
        """
        """
        log.info("TradeshowReportView:post")
        try:
            # Get tradehow and exhibitors
            tradeshowID = request.POST.get("tradeshowID")    
            log.info("TradeshowReportView:post, tradeshowID: [%s]" % tradeshowID)        
            tradeshow = modelAPI.getTradeshowByID(tradeshowID)
            if not tradeshow:
                raise ReportException(errorCodes.TRADESHOW_NOT_EXISTS, "Tradeshow not exists")
            log.info("TradeshowReportView:post, tradeshow: [%s]" % tradeshow)        
            exhibitors = modelAPI.getExhibitorsByTradeshow(tradeshow)
            if not exhibitors:
                raise ReportException(errorCodes.TRADESHOW_DOES_NOT_HAVE_EXHIBITORS, "Tradeshow does not have exhibitors")
            log.info("TradeshowReportView:post, exhibitors: [%s]" % exhibitors)
            # Get reports for exhibitors
            exhibitorReports = []
            tradeshowName = tradeshow.name
            _tradeshowName = tradeshowName.replace(' ', '_')
            reportCount = ReportUrls.objects.filter(tradeshow=tradeshow).count()
            log.info("TradeshowReportView:post, reportCount: [%s]" % reportCount)
            if not reportCount:
                raise ReportException(errorCodes.TRADESHOW_NO_REPORTS_CONFIGURED, "No reports configured")
            reportBasePath = settings.TRADESHOW_REPORT_LOCATION
            server = settings.SERVER
            # Prepare the exhibitor reports information
            for exhibitor in exhibitors:
                log.info("TradeshowReportView:post, Processing exhibitor: [%s]" % exhibitor)
                exhibitorReport = dict()
                exhibitorName = exhibitor.name
                _exhibitorName = exhibitorName.replace(' ', '_')
                exhibitorReport['exhibitorName'] = exhibitorName
                # Verify if the report is generated for exhibitor
                reportPath = "%s/%s/%s" % (reportBasePath, _tradeshowName, _exhibitorName)
                log.info("TradeshowReportView:post, reportPath: [%s]" % reportPath)
                if not os.path.exists(reportPath):
                    log.info("TradeshowReportView:post, reportPath not exists")
                    exhibitorReport['reportStatus'] = "Not Generated"
                    exhibitorReport['reportLink'] = "#"
                    exhibitorReport['csvLink'] = "#"
                    exhibitorReport['pdfLink'] = "#"
                    exhibitorReports.append(exhibitorReport)
                    continue
                _files = os.listdir(reportPath)
                # TODO: Need to support other types as well
                files = filter(lambda x:x.endswith('.png'), _files)
                if not files:
                    log.info("TradeshowReportView:post, No png files present at reportPath")
                    exhibitorReport['reportStatus'] = "Not Generated"
                    exhibitorReport['reportLink'] = "#"
                    exhibitorReport['csvLink'] = "#"
                    exhibitorReport['pdfLink'] = "#"
                    exhibitorReports.append(exhibitorReport)
                    continue
                if len(files) != reportCount:
                    log.info("TradeshowReportView:post, Not all png files present at reportPath")
                    exhibitorReport['reportStatus'] = "Partially Generated"
                    exhibitorReport['reportLink'] = "#"
                    exhibitorReport['csvLink'] = "#"
                    exhibitorReport['pdfLink'] = "#"
                    exhibitorReports.append(exhibitorReport)
                    continue 
                # Generate the reportID
                _key = "%s#%s#%s" % (tradeshowName, exhibitorName, datetime.now())
                log.info("TradeshowReportView:post, reportID key: [%s]" % _key)
                reportID = base64.b64encode(_key)
                # Prepare the report, csv and pdf link
                log.info("TradeshowReportView:post, reportID: [%s]" % reportID)
                reportLink = "%s/tsadmin/view/exhibitor/report/?reportID=%s" % (server, reportID)
                csvLink = "%s/tsadmin/download/exhibitor/report/?reportID=%s&amp;format=csv&amp;t=%s" % (server, reportID, time.time())
                pdfLink = "%s/tsadmin/download/exhibitor/report/?reportID=%s&amp;format=pdf&amp;t=%s" % (server, reportID, time.time())
                exhibitorReport['reportStatus'] = "Generated"
                exhibitorReport['reportLink'] = reportLink
                exhibitorReport['csvLink'] = csvLink
                exhibitorReport['pdfLink'] = pdfLink
                log.info("TradeshowReportView:post, exhibitorReport: [%s]" %exhibitorReport)
                exhibitorReports.append(exhibitorReport)

            reportInfo = dict()
            reportInfo['reportCount'] = reportCount
            reportInfo['exhibitorReports'] = exhibitorReports
            return render_to_response("exhibitor_reports.html", reportInfo)
        except ReportException as ex:
            log.info("TradeshowReportView:post, ReportException, statusCode: [%s], Message: [%s]" % (ex.statusCode, ex.message))
            return render_to_response("exhibitor_reports.html", {'message': ex.message})
        except Exception as ex:
            log.info("TradeshowReportView:post, Exception, Error: [%s]" % (str(ex)))
            statusCode = errorCodes.TRADESHOW_REPORT_VIEW_EXCEPTION
            message = "Unable to get tradeshow reports."
            return render_to_response("exhibitor_reports.html", {'message': message})
