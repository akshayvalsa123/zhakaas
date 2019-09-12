import os
from datetime import datetime
import logging 

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic import View

from tradeshow.common import model_apis as modelAPI
from tradeshow.common import error_codes as errorCodes
from tradeshow.common.exceptions import LeadException

from api.models import Tradeshow

log = logging.getLogger(__name__)


class LeadsView(View):
    """View for leads.
    """
    def dispatch(self, request, *args, **kwargs):
        return super(LeadsView, self).dispatch(request, *args, **kwargs)
    
    def get(self, request):
        """
        """
        log.info("LeadsView:get")
        tradeshows = Tradeshow.objects.all()
        return render_to_response('leads_view.html', {'tradeshows': tradeshows}, context_instance = RequestContext(request))

    def post(self, request):
        """
        """
        try:
            log.info("LeadsView:post")
            # Get tradeshow and exhibitor
            tradeshowID = request.POST.get('tradeshowID', '').strip()
            tradeshow = modelAPI.getTradeshowByID(tradeshowID)
            if not tradeshow:
                raise LeadException(errorCodes.TRADESHOW_NOT_EXISTS, "Unable to get tradeshow.")
            log.info("LeadsView:post, tradeshow: [%s]" % tradeshow)
            exhibitorID = request.POST.get('exhibitorID', '').strip()
            exhibitor = modelAPI.getExhibitorByID(exhibitorID)
            if not exhibitor:
                raise LeadException(errorCodes.EXHIBITOR_NOT_EXISTS, "Unable to get exhibitor.")
            log.info("LeadsView:post, exhibitor: [%s]" % exhibitor)
            # Get fields mapping
            fieldsMapping = modelAPI.getFieldsMapping(tradeshow)
            if not fieldsMapping:
                raise LeadException(errorCodes.FIELDS_NOT_AVAILABLE, "Unable to get fields.")
            log.info("LeadsView:post, fieldsMapping: [%s]" % fieldsMapping)
            # Build the csv download link
            csvLink = "%s/tsadmin/download/csv/report/?tradeshowID=%s&exhibitorID=%s" % (settings.SERVER, tradeshowID, exhibitorID)
            templateData = {}
            templateData['exhibitor'] = exhibitor
            templateData['fieldsMapping'] = fieldsMapping
	    templateData['csvLink'] = csvLink
            return render_to_response('leads_view_template.html', templateData)
        except LeadException as ex:
            log.info("LeadsView:post, LeadException: statusCode: [%s], message: [%s]" % (ex.statusCode, ex.message))            
            message = "Unable to get data."
            return HttpResponse(ex.message)
        except Exception as ex:
            log.info("LeadsView:post, Exception: [%s]" % str(ex))            
            message = "Unable to get data."
            return HttpResponse(message)
