
import json
import logging
from datetime import datetime

from django.http import JsonResponse
from django.http import HttpResponse
from django.views.generic import View
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from api.models import UserLogin
from api.models import Exhibitor
from api.models import ExhibitorBooth
from api.models import Tradeshow
from api.models import FieldsMapping
from api.models import Mapping
from api.models import TradeshowSettings
from api.models import Qualifier
from api.models import QualifierQuestions
from api.models import DeviceDetails
from api.models import LeadMaster
from api.models import Lead
from api.models import LeadDetails
from api.models import LeadFields
from api.models import Answer

from api import error_codes as errorCodes

log = logging.getLogger(__name__)

class InfoView(View):
    """View for getting lead information.
    """
    
    def get(self, request):
        """
        """
        response = dict()
        leads = []
        log.info("In InfoView")
        response = {}
        
        leadIDs = request.GET['leadIDs']
        leadIDs = leadIDs.strip('').split(',')
        leadIDs = filter(None, leadIDs)
        for leadID in leadIDs:
            info = self._getLeadInformation(leadID)
            leads.append(info)
        response['leads'] = leads
        return JsonResponse(response)
        
    def _getLeadInformation(self, leadID):
        """
        """
        leadInfo = dict()
        leadInfo['leadID'] = leadID
        leadMaster = self._getObjectORNone(LeadMaster, leadID=leadID)
        if not leadMaster:            
            leadInfo['message'] = "Lead does not exists for leadID:%s" % leadID
            return leadInfo
        tradeshow = leadMaster.tradeshow
        leadInfo['tradeshowName'] = tradeshow.name
        leadInfo['tradeshowID'] = tradeshow.id
        leadFields = []
        _leadFields = LeadFields.objects.filter(lead=leadMaster)
        for _leadField in _leadFields:
            fieldInfo = {}
            fieldInfo['fieldName'] = _leadField.field.name
            fieldInfo['fieldValue'] = _leadField.fieldValue
            leadFields.append(fieldInfo)            
        leadInfo['leadFields'] = leadFields
        
        
        
    def _getObjectORNone(self, model, *args, **kwargs):
        modelName = model.__name__
        try:
            #log.info("In _getObjectORNone, Model: [%s] , args: [%s], kwargs: [%s]" % (modelName, args, kwargs))
            modelObj = model.objects.get(*args, **kwargs)
            #log.info("In _getObjectORNone, Model [%s], object exists, [%s]" % (modelName, modelObj))
            return modelObj
        except model.DoesNotExist:
            #log.info("In _getObjectORNone, Model [%s], object does not exists." % modelName)
            return None        
