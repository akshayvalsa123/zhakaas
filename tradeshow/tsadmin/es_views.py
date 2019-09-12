import logging
from django.db import transaction
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render_to_response

from tradeshow.common.model_apis import _getObjectORNone
from tradeshow.common.utils import _buildResponse
from api.models import Tradeshow
from api.models import Exhibitor
from api.models import QualifierQuestions
from api.models import Qualifier
from api.models import LeadMaster
from tsadmin.es_utils import getTradeshowIndexInfo
from tsadmin.es_utils import getESStatus


log = logging.getLogger(__name__)

def getESMapping(request):  
    """
    """
    tradeshowID = request.GET.get('tradeshowID', '').strip()
    log.info("getESMapping, tradeshowID: [%s]" % tradeshowID)

    tradeshow = _getObjectORNone(Tradeshow, id=tradeshowID)
    log.info("_getTradeshowQuestions, tradeshow: [%s]" % tradeshow)
    if not tradeshow:
        statusCode = -1
        message = "Tradeshow not exists."
        return render_to_response("es_mapping.html", {'questions': [], 'errorMessage': 'Tradeshow not exists.'})

    result = _getTradeshowQuestions(tradeshowID)
    log.info("getESMapping, _getTradeshowQuestions result: [%s]" % (result, ))
    status, message, questions = result
    if status != 0:
        return render_to_response("es_mapping.html", {'questions': [], 'errorMessage': message})

    result = getTradeshowIndexInfo(tradeshow.name)
    log.info("getESMapping, getTradeshowIndexInfo result: [%s]" % (result, ))
    status, lastExportMessage = result

    leadCount = LeadMaster.objects.filter(tradeshow=tradeshow).count()
    esStatus = getESStatus()
    _esStatus = 'YES' if esStatus else 'NO'
    return render_to_response("es_mapping.html", {'questions': questions, 'leadCount': leadCount, 'lastExport':lastExportMessage, 'ESRunning': _esStatus})

def saveESMapping(request):  
    """
    """
    try:
        postData = dict()
        fieldCount = 0
        for key in request.POST:
            postData[key] = request.POST[key].strip()
            if key.startswith('ESField_'):
                fieldCount += 1
                value = request.POST[key].strip()
                if not value:
                    status = -1
                    message = 'ES Mapping Field is mandatory.'
                    raise ValueError(message)
        result = _saveESMapping(postData, fieldCount)
        status, message, info = result
        if status != 0:
            raise ValueError(message)
        response = _buildResponse(status, message)
        return JsonResponse(response)
    except ValueError as ex:
        log.info("saveESMapping: Unable to save ES mapping. ValueError: [%s]" % str(ex))
        response = _buildResponse(status, message)
    except Exception as ex:
        log.info("saveESMapping: Unable to save ES mapping. Exception: [%s]" % str(ex))
        status = -1
        message = 'Unable to save ES Mapping.'
        response = _buildResponse(status, message)
    return JsonResponse(response)
    
def _saveESMapping(postData, fieldCount):
    """
    """
    statusCode = 0
    message = 'ES Mapping save successful.'
    questions = []
    try:
        with transaction.atomic():
            tradeshowID = postData.get('tradeshowID')
            tradeshow = _getObjectORNone(Tradeshow, id=tradeshowID)
            log.info("_saveESMapping, tradeshow: [%s]" % tradeshow)
            if not tradeshow:
                statusCode = -1
                message = "Tradeshow not exists."
                raise ValueError(message)
            for index in range(1, fieldCount+1):
                mappingValue = postData["ESField_%s" % index]
                quaifierIDs = postData["qualifierIDs_%s" % index]
                quaifierIDs = quaifierIDs.split(',')
                quaifierIDs = [int(x) for x in quaifierIDs]
                for quaifierID in quaifierIDs:
                    qualifierQuestion = _getObjectORNone(QualifierQuestions, id=quaifierID)                
                    qualifierQuestion.mapping = mappingValue
                    qualifierQuestion.save()
        return (statusCode, message, [])    
    except ValueError as ex:
        log.info("_getTradeshowQuestions: Unable to get tradehsow questions. ValueError: [%s]" % str(ex))
    except Exception as ex:
        log.info("_getTradeshowQuestions: Unable to get tradehsow questions. Exception: [%s]" % str(ex))
        statusCode = -1
        message = "Unable to get tradehsow questions."
    return (statusCode, message, [])

def _getTradeshowQuestions(tradeshowID):
    """
    """
    statusCode = 0
    message = ''
    questions = []
    try:
        tradeshow = _getObjectORNone(Tradeshow, id=tradeshowID)
        log.info("_getTradeshowQuestions, tradeshow: [%s]" % tradeshow)
        if not tradeshow:
            statusCode = -1
            message = "Tradeshow not exists."
            raise ValueError(message)

        exhibitors = Exhibitor.objects.filter(tradeshow=tradeshow)
        qualifiers = Qualifier.objects.filter(exhibitor__in=exhibitors)
        qualifierQuestions = QualifierQuestions.objects.filter(qualifier__in=qualifiers)
        questionsInfo = {}
        for qualifierQuestion in qualifierQuestions:
            qualifierType = qualifierQuestion.qualifier.qualifierTypeID.qualifierType
            qualifierName = qualifierQuestion.qualifier.qualifierName
            question = qualifierQuestion.question.question
            mapping = qualifierQuestion.mapping if qualifierQuestion.mapping else ''
            _id = qualifierQuestion.id
            
            if not questionsInfo.has_key(qualifierType):
                questionsInfo[qualifierType] = {}

            if not questionsInfo[qualifierType].has_key(qualifierName):
                questionsInfo[qualifierType][qualifierName] = {}
            if not questionsInfo[qualifierType][qualifierName].has_key(question):         
                questionsInfo[qualifierType][qualifierName][question] = {'mapping': mapping, 'ids':[]}

            questionsInfo[qualifierType][qualifierName][question]['ids'].append(str(_id))
            #questionsInfo[qualifierType][qualifierName][question]['mapping'] = mapping
        log.info("_getTradeshowQuestions: questionsInfo: [%s]" % questionsInfo)
        questions = []
        for qualifierType in questionsInfo:
            for qualifierName in questionsInfo[qualifierType]:
                for question in questionsInfo[qualifierType][qualifierName]:
                    _mapping = questionsInfo[qualifierType][qualifierName][question]['mapping']
                    ids = questionsInfo[qualifierType][qualifierName][question]['ids']
                    _ids = ','.join(ids)
                    _question = (qualifierType, qualifierName, question, _mapping, _ids)
                    questions.append(_question)
        questions.sort()
        log.info("_getTradeshowQuestions: questions: [%s]" % questions)
        return (statusCode, message, questions)    
    except ValueError as ex:
        log.info("_getTradeshowQuestions: Unable to get tradehsow questions. ValueError: [%s]" % str(ex))
    except Exception as ex:
        log.info("_getTradeshowQuestions: Unable to get tradehsow questions. Exception: [%s]" % str(ex))
        statusCode = -1
        message = "Unable to get tradehsow questions."
    return (statusCode, message, questions)
