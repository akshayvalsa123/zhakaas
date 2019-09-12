import os
from subprocess import call, check_output
import re
import urllib
import logging
import pdfkit
import csv

from django.conf import settings
from api.models import Tradeshow
from api.models import Exhibitor
from api.models import ReportUrls
from api.reports import getReportUrls
from api.leads import getLeads
from tradeshow.common.utils import UnicodeWriter

log = logging.getLogger(__name__)
hdlr = logging.StreamHandler()
#hdlr = logging.FileHandler('/tmp/import_ts.log')
#hdlr = logging.handlers.RotatingFileHandler('/tmp/logs/add_artifact_creatorID.log', maxBytes=10*1024*1024, backupCount=500)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
log.addHandler(hdlr)
log.setLevel(logging.INFO)

def generateTradeshowReports(tradeshowName):
    """
    """
    try:
        log.info("generateTradeshowReports: tradeshowName: [%s]" % tradeshowName)
        # Get the tradeshow
        if not tradeshowName:
            log.info("generateTradeshowReports:Tradeshow name is empty")
            statusCode = -1
            msg = "Tradeshow name is empty"
            raise ValueError(msg)
        tradeshow = _getObjectORNone(Tradeshow, name=tradeshowName)        
        if not tradeshow:
            log.info("generateTradeshowReports:Tradeshow does not exists, tradeshowName: [%s]" % tradeshowName)
            statusCode = -1     
            msg = "Tradeshow with name %s does not exists." % tradeshowName
            raise ValueError(msg)

        # Get the phanthom script and report path
        phantomscript = settings.TRADESHOW_REPORT_JS
        reportPath = settings.TRADESHOW_REPORT_LOCATION
        # Define height and width
        width = "1440"
        height = "900"

        # Get the
        tradeshowID = tradeshow.id
        reportUrlInfo = getReportUrls(tradeshowID)
        log.info("generateTradeshowReports: reportUrlInfo: [%s]" % reportUrlInfo)
        status = reportUrlInfo.get('status')
        exhibitorReports = dict()
        if status != 0:
            log.info("generateTradeshowReports: Unable to get report urls.")
        else:
            exhibitorReports = reportUrlInfo['exhibitorReports']        

        # Get the report urls
        reportUrls = ReportUrls.objects.filter(tradeshow=tradeshow)
        if not reportUrls:
            log.info("generateTradeshowReports:No report urls exists")
            statusCode = -1     
            msg = "generateTradeshowReports:No report urls exists"
            raise ValueError(msg)
        # Get the exhibitors
        exhibitors = Exhibitor.objects.filter(tradeshow=tradeshow)
        if not exhibitors:
            log.info("generateTradeshowReports:No exhibitors exists")
            statusCode = -1     
            msg = "No exhibitors exists"
            raise ValueError(msg)
        # RE for exhibitor query
        expat = re.compile("'(exhibitor:.*?)'")
        _tradeshowName = tradeshowName.replace(' ', '_')
        tradeshowReportPath = reportPath + os.sep + _tradeshowName
        if not os.path.exists(tradeshowReportPath):
            os.makedirs(tradeshowReportPath)
            log.info("generateTradeshowReports: Created tradeshowReportPath: [%s]" % tradeshowReportPath)

        # Build the reports for each exhibitor
        for exhibitor in exhibitors:
            exhibitorName = exhibitor.name
            exhibitorID = exhibitor.id
            log.info("generateTradeshowReports: Processing Exhibitor: [%s]" % exhibitorName)
            # Prepare the report directory for exhibitor if not exists.
            exhibitorReportPath = tradeshowReportPath + os.sep + exhibitorName.replace(' ', '_')
            if not os.path.exists(exhibitorReportPath):
                os.makedirs(exhibitorReportPath)
                log.info("generateTradeshowReports: Created exhibitorReportPath: [%s]" % exhibitorReportPath)
            # Build the filter query for exhibitor
            _exhibitorName = '"%s"' % exhibitorName
            _exhibitorName = urllib.quote(_exhibitorName)
            _query = "exhibitor:%s" % _exhibitorName
            log.info("generateTradeshowReports: Exhibitor Query: [%s]" % _query)
            # Generate the reports 
            for reportUrl in reportUrls:
                reportName = reportUrl.name
                # Build the report url for the exhibitor
                _url = reportUrl.url
                log.info("generateTradeshowReports: Processing Report: [%s]" % reportName)
                _results = expat.findall(_url)
                if not _results:
                    log.info("generateTradeshowReports: Exhibitor filter not available in report url. Report [%s] will not be generated." % reportName)
                    continue
                _exquery = _results[0]
                _reportUrl = _url.replace(_exquery, _query)
                log.info("generateTradeshowReports: Generated Report Url: [%s]" % _reportUrl)
                reportFile = exhibitorReportPath + os.sep + reportName.replace(' ', '_') + ".png"
                log.info("generateTradeshowReports: Creating report file: [%s]" % reportFile)
                #call(['phantomjs', phantomscript, _reportUrl, width, height, reportFile])
                log.info("generateTradeshowReports: File created.")
            # generate PDF
            reportDetails = exhibitorReports.get(exhibitorName)
            log.info("generateTradeshowReports: reportDetails: [%s]" % reportDetails)
            if reportDetails:
                reportLink = reportDetails['reportLink']
                if reportLink != "#":
                    pdfFile = exhibitorReportPath + os.sep + exhibitorName + ".pdf"
                    log.info("generateTradeshowReports: generating pdf, pdfFile: [%s]" % pdfFile)
                    pdfkit.from_url(reportLink, pdfFile)
                else:
                    log.info("generateTradeshowReports: PDF not generated , Exhibitor reportStatus is [%s]" % reportStatus)
            else:
                log.info("generateTradeshowReports: PDF not generated , Exhibitor reportDetails not available.")

            # Generate CSV
            result = getLeads(tradeshowID, exhibitorID, includeQuestions=True, includeDetails=True, format='csv')
            log.info("generateTradeshowReports: getLeads , result: [%s]" % (result,))
            status, message, csvRows = result
            if status != 0:
                log.info("generateTradeshowReports: CSV not generated , Exhibitor csvData not available.")
            csvFile = exhibitorReportPath + os.sep + exhibitorName + ".csv"
            log.info("generateTradeshowReports: generating csv, csvFile: [%s]" % csvFile)
            try:
                with open(csvFile, 'wb') as f:
                    writer = UnicodeWriter(f)
                    writer.writerows(csvRows)
            except Exception as ex:
                log.info("generateTradeshowReports: CSV not generated , Exception: [%s]" % str(ex))
                raise ex
    except ValueError as ex:
        log.info("generateTradeshowReports: ValueError Exception: [%s]" % str(ex))
        raise ex
    except Exception as ex:
        log.info("generateTradeshowReports: Exception: [%s]" % str(ex))
        statusCode = -1
        message = "Got Exception in generateTradeshowReports, Exception: [%s]" % str(ex)  
        raise ex

def _getObjectORNone(model, *args, **kwargs):
    modelName = model.__name__
    try:
        log.info("In _getObjectORNone, Model: [%s] , args: [%s], kwargs: [%s]" % (modelName, args, kwargs))
        modelObj = model.objects.get(*args, **kwargs)
        log.info("In _getObjectORNone, Model [%s], object exists, [%s]" % (modelName, modelObj))
        return modelObj
    except model.DoesNotExist:
        log.info("In _getObjectORNone, Model [%s], object does not exists." % modelName)
        return None

#tradeshowName = "Times Property Expo"
#generateTradeshowReports(tradeshowName)

