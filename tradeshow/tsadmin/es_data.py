import logging
from datetime import datetime
from django.conf import settings

from api.models import Tradeshow
from api.models import Exhibitor
from api.models import ExhibitorBooth
from api.models import Lead
from api.models import LeadFields
from api.models import LeadMaster
from api.models import LeadDetails
from api.models import Answer
from api.models import QualifierQuestions
from tradeshow.common.model_apis import _getObjectORNone

log = logging.getLogger(__name__)

def getTradeshowESData(tradeshowID, exhibitorID):
    """
    """
    status, message = 0, ''
    try:
        tradeshow = _getObjectORNone(Tradeshow, id=tradeshowID)
        if exhibitorID == "all":
            _ids = Exhibitor.objects.filter(tradeshow=tradeshow).values_list('id')
            exhibitorIDs = [item[0] for item in _ids]
        else:
            exhibitorIDs = [exhibitorID]
        exhibitorLeads = []
        for exhibitorID in exhibitorIDs[:1]:         #TODO: Remove the temporary limit
            exhibitor = _getObjectORNone(Exhibitor, id=exhibitorID)
            exhibitorBooths = ExhibitorBooth.objects.filter(exhibitor=exhibitor)
            leads = Lead.objects.filter(exhibitorBooth__in = exhibitorBooths)[:10] #TODO: Remove the temporary limit
            leadInfoList = []
            for lead in leads:
                leadMaster = lead.leadMaster
                leadDetails = lead.leadDetails		
                fields = {}
                leadFields = LeadFields.objects.filter(lead=leadMaster)
                for leadField in leadFields:
                    fields[leadField.field.name] = leadField.fieldValue
                questionAnswers = {}
                answers = Answer.objects.filter(lead=lead)
                for answer in answers:
                    answerValue = answer.answer
                    qualifierQuestion = answer.question
                    question = qualifierQuestion.question.question.lower()
                    if qualifierQuestion.mapping:
                        mappedQuestion = qualifierQuestion.mapping
                    else:
                        mappedQuestion = question.replace(' ', '_')
                    questionAnswers[mappedQuestion] = answerValue
                leadInfo = {}
                leadInfo["tradeshow"] = tradeshow.name
                leadInfo["exhibitor"] = exhibitor.name
                leadInfo["username"] = lead.exhibitorBooth.userName.userName
                leadInfo["leadID"] = leadMaster.leadID		
                leadInfo["captureTime"] = datetime.strftime(leadDetails.captureTime, settings.TRADESHOW_TIME_FORMAT)
                leadInfo["leadType"] = leadDetails.leadType
                leadInfo["scanType"] = leadDetails.scanType
                leadInfo.update(fields)			
                leadInfo.update(questionAnswers)
                leadInfoList.append(leadInfo)

            exhibitorData = {'leads': leadInfoList}
            exhibitorData["tradeshow"] = tradeshow.name
            exhibitorData["exhibitor"] = exhibitor.name
            exhibitorLeads.append(exhibitorData)
        ESData = exhibitorLeads
        return (0, '', ESData)
    except Exception as ex:
        log.info("getTradeshowESData: Unable to get ES Data, Exception :[%s]" % str(ex))
        return (-1, 'Unable to get ES Data', [])
        
