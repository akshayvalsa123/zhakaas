import os
from datetime import datetime
import logging
import base64

from django.conf import settings
from django.http import JsonResponse
from api.models import Tradeshow
from api.models import Exhibitor
from api.models import ReportUrls

log = logging.getLogger(__name__)

def getReportUrls(tradeshowID):
    """
    """
    response = {}
    tradeshow = _getObjectORNone(Tradeshow, id=tradeshowID)
    if not tradeshow:
        response['status'] = -1
        response['message'] = 'Tradeshow not exists'
        return response

    exhibitors = Exhibitor.objects.filter(tradeshow=tradeshow)
    if not exhibitors:
        response['status'] = -1
        response['message'] = 'Tradeshow does not have exhibitors'
        return response
    
    tradeshowName = tradeshow.name
    _tradeshowName = tradeshowName.replace(' ', '_')
    reportCount = ReportUrls.objects.filter(tradeshow=tradeshow).count()
    if not reportCount:
        response['status'] = -1
        response['message'] = 'No reports configured'
        return response
    exhibitorReports = dict()
    reportBasePath = settings.TRADESHOW_REPORT_LOCATION
    server = settings.SERVER
    for exhibitor in exhibitors:
        exhibitorReport = dict()
        name = exhibitor.name
        _name = name.replace(' ', '_')
        exhibitorReport['exhibitorName'] = name
        reportPath = "%s/%s/%s" % (reportBasePath, _tradeshowName, _name)
        if not os.path.exists(reportPath):
            exhibitorReport['reportStatus'] = "Not Generated"
            exhibitorReport['reportLink'] = "#"
            continue
        _files = os.listdir(reportPath)
        files = filter(lambda x:x.endswith('.png'), _files)
        if not files:
            exhibitorReport['reportStatus'] = "Not Generated"
            exhibitorReport['reportLink'] = "#"
            continue
        if len(files) != reportCount:
            exhibitorReport['reportStatus'] = "Partially Generated"
            exhibitorReport['reportLink'] = "#"
            continue 
        _key = "%s#%s#%s" % (tradeshowName, name, datetime.now())
        reportID = base64.b64encode(_key)
        reportLink = "%s/api/view/report?reportID=%s" % (server, reportID)
        exhibitorReport['reportStatus'] = "Generated"
        exhibitorReport['reportLink'] = reportLink
        exhibitorReports[name] = exhibitorReport

    response['status'] = 0
    response['message'] = ''
    response['exhibitorReports'] = exhibitorReports
    return response


def _getObjectORNone(model, *args, **kwargs):
    modelName = model.__name__
    try:
        #log.info("In _getObjectORNone, Model: [%s] , args: [%s], kwargs: [%s]" % (modelName, args, kwargs))
        modelObj = model.objects.get(*args, **kwargs)
        #log.info("In _getObjectORNone, Model [%s], object exists, [%s]" % (modelName, modelObj))
        return modelObj
    except model.DoesNotExist:
        #log.info("In _getObjectORNone, Model [%s], object does not exists." % modelName)
        return None
