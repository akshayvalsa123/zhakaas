import logging

from django.views.generic import View
from django.shortcuts import render_to_response
from api.models import Tradeshow
from django.http import JsonResponse
from tradeshow.common.utils import _buildResponse
from tradeshow.common.model_apis import _getObjectORNone
from tsadmin.es_utils import exportToES

log = logging.getLogger(__name__)


class ExportReportView(View):
    """
    """
   
    def get(self, request):
        """
        """
        log.info("ExportReportView:get")
        tradeshows = Tradeshow.objects.all()
        return render_to_response('export_report_view.html', {'tradeshows': tradeshows})


    def post(self, request):
        """
        """
        try:
            status, message = 0, 'Export data to ES successful.'
            log.info("ExportReportView:post")
            tradeshowID = request.POST.get('tradeshowID')
            tradeshow = _getObjectORNone(Tradeshow, id=tradeshowID)
            log.info("ExportReportView:post, tradeshow: [%s]" % tradeshow)
            if not tradeshow:
                statusCode = -1
                message = "Tradeshow not exists."
                response = _buildResponse(status, message)
                return JsonResponse(response)

            result = exportToES(tradeshowID)
            log.info("ExportReportView:post, exportToES, result: [%s]" % (result,))
            status, message = result
            response = _buildResponse(status, message)
            return JsonResponse(response)
        except Exception as ex:
            log.info("ExportReportView:post, Unable to export data to ES, Exception: [%s]" % str(ex))
            status, message = -1, 'Unable to export data to ES.'
            response = _buildResponse(status, message)         
        return JsonResponse(response)
