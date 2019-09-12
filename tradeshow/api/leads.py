import logging
from datetime import datetime
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

def getLeads(tradeshowID, exhibitorID, includeQuestions=False, includeDetails=False, format=None):
    """
    """
    statusCode = 0
    message = ''
    if not tradeshowID:
        statusCode = -1
        message = "tradeshowID not provided."
        response = (statusCode, message, [])
        return response
    try:
        tradeshowID = int(tradeshowID)
    except:
        statusCode = -1
        message = "Invalid tradeshowID provided."
        response = (statusCode, message, [])
        return response

    tradeshow = _getObjectORNone(Tradeshow, id=tradeshowID)
    if not tradeshow:
        statusCode = -1
        message = "Tradehsow does not exists."
        response = (statusCode, message, [])
        return response

    if not exhibitorID:
        statusCode = -1
        message = "exhibitorID not provided."
        response = (statusCode, message, [])
        return response
    try:
        exhibitorID = int(exhibitorID)
    except:
        statusCode = -1
        message = "Invalid exhibitorID provided."
        response = (statusCode, message, [])
        return response

    csvHeaders = []
    # Get the mapping and field sequences
    mapping = _getObjectORNone(Mapping, tradeshow=tradeshow)
    fieldSequences = FieldsMapping.objects.filter(mapping=mapping).values_list('field__name', 'field__displayName','fieldSeq').order_by('fieldSeq')
    # Build the csv headers for fields
    for fieldSequence in fieldSequences:
        name, displayName, seq = fieldSequence
        if name == 'badgeData':
            continue
        csvHeaders.append(displayName)
    count = 0
    csvRows = []
    exhibitor = _getObjectORNone(Exhibitor, id=exhibitorID)
    exhibitorBooths = ExhibitorBooth.objects.filter(exhibitor=exhibitor)
    leads = Lead.objects.filter(exhibitorBooth__in = exhibitorBooths)[:10]
    totalRecords = leads.count()
    if includeDetails:
        csvHeaders.extend(['Capture Time', 'Lead Type', 'Scan Type'])
    # Build questions sequences and csv headers for questions
    questionSeqIDs = []
    if includeQuestions:
        qualifiers = Qualifier.objects.filter(exhibitor=exhibitorID).order_by('screenNo')
        for qualifier in qualifiers:
            _questions = QualifierQuestions.objects.filter(qualifier=qualifier).order_by('seq')
            for _question in _questions:
                header = "%s#%s" % (qualifier.qualifierName, _question.question.question)
                csvHeaders.append(header)
                questionSeqIDs.append(_question.id)
    for lead in leads:
        count += 1
        leadMaster = lead.leadMaster
        #leadDetails = lead.leadDetails		
        fields = {}
        leadFields = LeadFields.objects.filter(lead=leadMaster)
        for leadField in leadFields:
            fields[leadField.field.name] = leadField.fieldValue

        csvRow = []
        for fieldSequence in fieldSequences:
            name, displayName, seq = fieldSequence
            if name == 'badgeData':
                continue
            value = fields[name]
            if name in ['firstName', 'lastName', 'name']:
                value = value.title()
            csvRow.append(value)        
        if includeDetails:
            leadDetails = lead.leadDetails
            captureTime = leadDetails.captureTime if leadDetails.captureTime else ''
            if captureTime and format in ['csv']:
                captureTime = datetime.strftime(captureTime, settings.TRADESHOW_TIME_FORMAT)
            leadType = leadDetails.leadType if leadDetails.leadType else ''
            scanType = leadDetails.scanType if leadDetails.scanType else ''
            csvRow.extend([captureTime, leadType, scanType])            
        if includeQuestions:
            # Get the questions answers
            answerMapping = dict()
            answers = Answer.objects.filter(lead=lead)
            if format in ['csv']: # Change the checkbox values to Yes and No
                for answer in answers:
                    answerValue = answer.answer if answer.answer else ''
                    if answer.question.question.widgetName == "Checkbox":
                        if answerValue == "1":
                            answerValue = "Yes"
                        elif answerValue == "0":
                            answerValue = "No"
                    answerMapping[answer.question.id] = answerValue
            else:
                for answer in answers:
                    answerMapping[answer.question.id] = answer.answer if answer.answer else ''
            for questionSeqID in questionSeqIDs:
                _answer = answerMapping.get(questionSeqID, '')
                csvRow.append(_answer)
        csvRows.append(csvRow)
    rows = [csvHeaders] + csvRows
    return (statusCode, message, rows)


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

