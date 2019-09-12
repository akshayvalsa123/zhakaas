import logging
from django.conf import settings
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

log = logging.getLogger(__name__)

def getLeadsByExhibitorBooth(exhibitorBooth):
    """
    """
    try:
        exhibitor = exhibitorBooth.exhibitor
        tradeshow = exhibitor.tradeshow
        # Get the mapping and field sequences
        mapping = _getObjectORNone(Mapping, tradeshow=tradeshow)
        fieldSequences = FieldsMapping.objects.filter(mapping=mapping).values_list('field__name', 'field__displayName','fieldSeq').order_by('fieldSeq')
        leads = Lead.objects.filter(exhibitorBooth=exhibitorBooth)
        count = 0
        allLeads = []
        for lead in leads:        
            count += 1
            leadMaster = lead.leadMaster        
            #leadDetails = lead.leadDetails		
            fields = {}
            leadFields = LeadFields.objects.filter(lead=leadMaster)
            for leadField in leadFields:
                fields[leadField.field.name] = leadField.fieldValue
            fieldList = []
            for fieldSequence in fieldSequences:
                name, displayName, seq = fieldSequence
                if name == 'badgeData':
                    continue
                value = fields[name]
                if name in ['firstName', 'lastName', 'name']:
                    value = value.title()
                fieldList.append({'fieldName': displayName, 'fieldValue': value})
            leadDetails = lead.leadDetails
            captureTime = leadDetails.captureTime if leadDetails.captureTime else ''
            if captureTime and format in ['csv']:
                captureTime = datetime.strftime(captureTime, settings.TRADESHOW_TIME_FORMAT)
            leadType = leadDetails.leadType if leadDetails.leadType else ''
            scanType = leadDetails.scanType if leadDetails.scanType else ''
            # Build the answer mapping
            answerMapping = dict()
            answers = Answer.objects.filter(lead=lead)
            for answer in answers:
                answerMapping[answer.question.id] = answer.answer if answer.answer else ''
            questions = []
            qualifiers = Qualifier.objects.filter(exhibitor=exhibitor).order_by('screenNo')
            for qualifier in qualifiers:
                _questions = QualifierQuestions.objects.filter(qualifier=qualifier).order_by('seq')
                screenNo = qualifier.screenNo
                for _question in _questions:
                    info = {}
                    info['question'] = _question.question.question
                    info['answer'] = answerMapping.get(_question.id)
                    info['questionID'] = _question.id
                    info['screenNo'] = screenNo
                    info['questionSeq'] = _question.seq
                    questions.append(info)
            leadInfo = {}
            leadInfo['leadID'] = leadMaster.leadID
            leadInfo['fields'] = fieldList
            leadInfo['questions'] = questions
            leadInfo['captureTime'] = captureTime
            leadInfo['leadType'] = leadType
            leadInfo['scanType'] = scanType
            allLeads.append(leadInfo)
        return allLeads
    except Exception as ex:
        log.info("In getLeadsByExhibitorBooth, Exception." % str(ex))
        raise ex
        return []

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
