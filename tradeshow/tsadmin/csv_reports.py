import os
import logging
import csv
from django.conf import settings
from django.http import HttpResponse

from tradeshow.common.model_apis import _getObjectORNone
from api.models import Exhibitor
from api.leads import getLeads
from tradeshow.common.utils import UnicodeWriter


log = logging.getLogger(__name__)

def downloadCSVReport(request):
    """
    """
    try:
        tradeshowID = int(request.GET['tradeshowID'].strip())
        exhibitorID = int(request.GET['exhibitorID'].strip())
        exhibitor = _getObjectORNone(Exhibitor, id=exhibitorID)
        if not exhibitor:
            return HttpResponse("Failed to download csv. Exhibitor not exists.")
        result = getLeads(tradeshowID, exhibitorID, includeQuestions=True, includeDetails=True, format="csv")
        statusCode, message, rows = result
        log.info("downloadCSVReport: statusCode:[%s], message[%s], leadCount : [%s]" % (statusCode, message, len(rows) ))
        if statusCode == 0:
            _ids = '%s_%s' % (tradeshowID, exhibitorID)
            CSVReportPath = settings.TRADESHOW_REPORT_LOCATION + os.sep + "csv"
            csvFile = CSVReportPath + os.sep + _ids + ".csv"
            log.info("generateTradeshowReports: generating csv, csvFile: [%s]" % csvFile)
            try:
                with open(csvFile, 'wb') as f:
                    writer = UnicodeWriter(f)
                    writer.writerows(rows)
                data = open(csvFile).read()
                response = HttpResponse(data, content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename=leads.csv'
                return response
            except Exception as ex:
                log.info("generateTradeshowReports: CSV not generated , Exception: [%s]" % str(ex))
                raise ex
        else:
            return HttpResponse("Unable to download csv. Error- %s " % message)
    except Exception as ex:
        raise ex
        log.info("downloadCSVReport: Exception: [%s]" % str(ex))
        return HttpResponse("Failed to download csv.")
