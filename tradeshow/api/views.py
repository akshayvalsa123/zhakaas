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


from api.field_mappings import modelFieldMappings, validationFieldMappings
from api import error_codes as errorCodes

log = logging.getLogger(__name__)

class LoginView(View):
    """View for login.
    """
    
    def get(self, request):
        """
        """
        statusCode = 0
        message = ""
        log.info("LoginView:get")
        response = {}
        try:
            # Fetch user credentials from request.
            username = request.GET.get('username', '').strip()
            password = request.GET.get('password', '').strip()            
            if not (username and password): 
                statusCode = errorCodes.EMPTY_LOGIN_CREDENTIALS
                message = "Username/Password can not be empty."
                raise ValueError("Username/Password can not be empty.")

            # Validate User Login
            userLogin = UserLogin.objects.get(userName=username, password=password)
            if not userLogin:
                statusCode = errorCodes.AUTHENTICATION_FAILED
                message = "User authentication failed."
                raise ValueError("User authentication failed.")
            
            # Get the exhibitor booth
            exhbBooth = ExhibitorBooth.objects.get(userName=userLogin)
            
            # Get the exhibitor & tradeshow
            exhibitor = exhbBooth.exhibitor
            tradeshow = exhibitor.tradeshow
            
            # Get fields for tradeshow
            fields = dict()
            tradeshowMapping = tradeshow.mapping_set.get()
            fieldMappings = FieldsMapping.objects.filter(mapping=tradeshowMapping).order_by('fieldSeq')
            fields['total'] = fieldMappings.count()        
            fieldsData = []
            for fieldMapping in fieldMappings:
                data = dict()
                data['fieldName'] = fieldMapping.field.name
                data['fieldDisplayName'] = fieldMapping.field.displayName            
                data['fieldSeq'] = fieldMapping.fieldSeq
                fieldsData.append(data)
            fields['data'] = fieldsData
            response['fields'] = fields

            # Get tradeshow settings         
            settingsData = tradeshow._getSettings()
            settings = dict()
            settings['data'] = settingsData
            settings['total'] = len(settingsData)
            response['settings'] = settings

            # Get tradeshow qualifiers for exhibitor        
            qualifierTypes = dict()
            exhibitorQualifiers = Qualifier.objects.filter(exhibitor=exhibitor)
            for exhibitorQualifier in exhibitorQualifiers:
                data = dict()
                qualifierType = exhibitorQualifier.qualifierTypeID.qualifierType
                data['qualifierName'] =  exhibitorQualifier.qualifierName
                data['screenNo'] = exhibitorQualifier.screenNo
                data['totalQuestions'] = exhibitorQualifier.totalQuestions
                questionsData = []
                questions = exhibitorQualifier.questions.order_by('QualifierQuestions.seq')
                for question in questions:
                    questionInfo = dict()   
                    questionInfo['question'] = question.question
                    questionInfo['widget'] = question.widgetName
                    questionInfo['option'] = question.options
                    # TODO : Calling QualifierQuestions can be avoided.
                    qualifierQuestion = QualifierQuestions.objects.get(qualifier=exhibitorQualifier, question=question)
                    questionInfo['seq'] = qualifierQuestion.seq
                    questionInfo['qualifierQuestionID'] = qualifierQuestion.id
                    questionsData.append(questionInfo)
                data['questions'] = questionsData            
                qualifierTypes.setdefault(qualifierType, []).append(data)            
            
            qualifiersData = []
            for qualifierType in qualifierTypes:
                qualifierInfo = dict()
                qualifierInfo['qualifierType'] = qualifierType
                qualifierInfo['total'] = len(qualifierTypes[qualifierType])
                qualifierInfo['data'] = qualifierTypes[qualifierType]
                qualifiersData.append(qualifierInfo)
                
            qualifiers = dict()    
            qualifiers['data'] = qualifiersData
            qualifiers['total'] = len(qualifiersData)
            response['qualifiers'] = qualifiers        
            response['tradeshowInfo'] = tradeshow._getInfo()
            response['exhibitorInfo'] = exhibitor._getInfo()
        except ValueError as ex:
            log.info("LoginView:get, ValueError Exception: [%s]" % str(ex))           
        except Exception as ex:
            log.info("LoginView:get, Exception: [%s]" % str(ex))           
            statusCode = errorCodes.Login_VIEW_EXCEPTION
            message = "Error in login."
        _response = self._buildResponse(statusCode, message, moreInfo=response)
        return JsonResponse(_response)

    def _buildResponse(self, statusCode, message, moreInfo=None):
        """
        """
        response = dict()
        response['response'] = {'message': message}
        response['responseHeader'] = dict()
        response['responseHeader']['status'] = statusCode
        if moreInfo:
            response['response'].update(moreInfo)
        return response

class UploadView(View):
    """View for upload.
       Sample Data :: 
       {
            "tradeshowID": "1345",
            "exhibitorID": "1456",
            "userName": "dlf",
            "deviceName": "akshay-mi",
            "leads": [
                      { "leadID": "b978520d-e13a-4b31-bfdd-9e6659a2c6fd",   
                        "captureTime": "09/20/2016 00:10:35",
                        "leadSyncStatus": "0",
                        "syncID": "0",
                        "leadFields": [{
                                        "fieldName": "FirstName",
                                        "fieldValue": "amol",
                                        }, {
                                        "fieldName": "LastName",
                                        "fieldValue": "bhagwat",
                                        }],
                        "leadAnswers": [{
                                    "qualifierQuestionID":"123123",
                                    "answerValue": "1",
                                     }, 
                                     {
                                    "qualifierQuestionID":"34535345",
                                    "answerValue": "1",
                                   }]

                    },{...}]
       }        
    """
    def get(self, request):
        """
        """
        response = {"status":100, "messages":["GET method not allowed"]}        
        return JsonResponse(response)
        
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(UploadView, self).dispatch(request, *args, **kwargs)
            
    def post(self, request):
        """Handles lead upload request.
        """
        leadIDs = {}
        response = _getDefaultresponse()
        leadsData = json.loads(request.body)		
        #return JsonResponse(leadsData)
		
        validationInfo = self._validateLeadsData(leadsData)
        log.info("UploadView:post, leadsData validationInfo: [%s]" % (validationInfo,))
        status, message, validatedLeadsData = validationInfo
        if status != 0: # Validation failed, return the error response.            
            response['responseHeader']['status'] = status
            response['response']['message'] = message
            return JsonResponse(response)
            
        # TODO: Disabling the device save , need to enble later.
        device = None
        if False:    
            # Save device details
            deviceDetails = validatedLeadsData['deviceDetails']
            log.info("UploadView:post, Saving Devicedetails")
            saveDeviceInfo = self._saveDevice(deviceDetails)
            log.info("UploadView:post, saveDeviceInfo: [%s]" % (saveDeviceInfo,))
            status, message, device = saveDeviceInfo
            if status != 0: # Validation failed, return the error response.            
                response['responseHeader']['status'] = status
                response['response']['message'] = message
                return JsonResponse(response)        
                    
        # Save leads
        exhibitorBooth = validatedLeadsData['exhibitorBooth']
        tradeshow = validatedLeadsData['tradeshow']
        leads = validatedLeadsData['leads']
        count = 0
        failedCount = 0
        savedLeads = []
        for lead in leads:
            count += 1
            # Save lead
            leadID = lead.get('leadID')
            log.info("==================== Start Saving Lead [%s], leadID [%s] ====================" % (count, leadID))
            saveLeadInfo = self._saveLead(lead, device, exhibitorBooth, tradeshow)
            log.info("UploadView:post, saveLeadInfo: [%s]" % (saveLeadInfo,))
            status, message, _lead = saveLeadInfo
            if status != 0:
                log.info("Lead processing will continue for next available lead.")
                failedCount += 1
            else:
                log.info("UploadView:post, Lead save successful, Lead: [%s]" % _lead)
                savedLeads.append(leadID)
            log.info("==================== End Saving Lead [%s], leadID [%s] ====================" % (count, leadID))
            # Process lead fields
        log.info("Total leads processed: [%s], Failed Leads: [%s]" % (count, failedCount))
        response['responseHeader']['status'] = 0
        response['response']['savedLeadsCount'] = len(savedLeads)
        response['response']['savedLeads'] = savedLeads
        response['response']['totalLeadsCount'] = count
        response['response']['failedLeadsCount'] = failedCount
        
        #response['response'][] = ''
                
        return JsonResponse(response)

    def _saveDevice(self, deviceDetails):
        """Add/Update the device.
        """        
        device = None
        log.info("UploadView:_saveDevice, deviceDetails: [%s]" % deviceDetails)
        try:
            validationInfo = _validateFields(deviceDetails, 'DeviceDetails', isModel=True)
            statusCode, message, validatedDeviceDetails = validationInfo
            if statusCode != 0:
                # Validation failed
                log.info("UploadView:_saveDevice, DeviceDetails validation failed.")
                return (statusCode, message, device)            
            log.info("UploadView:_saveDevice, DeviceDetails validation successful, validatedDeviceDetails: [%s]" % validatedDeviceDetails)            
            # TODO: Need to check if device already exists for the lead details            
            deviceID = deviceDetails['deviceID']
            device = self._getObjectORNone(DeviceDetails, deviceID=deviceID)
            if device:
                log.info("UploadView:_saveDevice, Device already exists, updating the device infromation.")
                # Set the id field such that save will update the record.
                validatedDeviceDetails['id'] = device.id
            else:
                log.info("UploadView:_saveDevice, Device does not exists, creating the device infromation.")
            log.info("UploadView:_saveDevice, Saving DeviceDetails")
            device = DeviceDetails(**validatedDeviceDetails)
            device.save()
            log.info("Device saved successfully, id/deviceID: [%s]/[%s]" % (device.id, device.deviceID))
            return (statusCode, message, device)
        except Exception as ex:
            log.info("UploadView:_saveDevice, Exception: [%s]" % str(ex))
            statusCode = errorCodes.SAVE_DEVICE_EXCEPTION
            message = "Unable to save device, Exception: [%s]" % str(ex)
            return (statusCode, message, None)
        
    def _saveLead(self, leadInfo, device, exhibitorBooth, tradeshow):
        """Add/update the lead.
        """     
        statusCode = 0
        message = ''   
        log.info("UploadView:_saveLead, leadInfo: [%s], device: [%s], exhibitorBooth: [%s]" % (leadInfo, device, exhibitorBooth))
        try:
            timeFormat = settings.TRADESHOW_TIME_FORMAT
            modelLeadFieldsInfo = dict()
            # Get the lead master and lead
            leadID = leadInfo.get('leadID')
            leadMaster = self._getObjectORNone(LeadMaster, leadID=leadID, tradeshow=tradeshow)        
            if leadMaster:
                log.info("UploadView:_saveLead, leadMaster exists, leadID: [%s]" % leadID)
                # Fetch the lead fields associated with leadMaster and prepare mapping
                modelLeadFields = LeadFields.objects.filter(lead=leadMaster)                
                for modelLeadField in modelLeadFields:
                    modelLeadFieldsInfo[modelLeadField.field.name] = modelLeadField
                # Get the lead associated with lead master
                lead = self._getObjectORNone(Lead, leadMaster=leadMaster, exhibitorBooth=exhibitorBooth)
            else:
                log.info("UploadView:_saveLead, leadMaster does not exists, new lead will be created. leadID: [%s]" % leadID)
                leadMaster = LeadMaster(leadID=leadID, tradeshow=tradeshow)
                leadMaster.save()
                lead = None
                
            # Get the tradeshow fields mapping
            tradeshowMapping = tradeshow.mapping_set.get()
            _fieldMappings = FieldsMapping.objects.filter(mapping=tradeshowMapping).order_by('fieldSeq')
            fieldMappings = dict()
            for _fieldMapping in _fieldMappings:
                fieldMappings[_fieldMapping.field.name] = _fieldMapping.field

            # Save the lead fields 
            leadFields = leadInfo.get('leadFields', [])
            for leadField in leadFields:
                # Fetch the field name received from request
                fieldName = leadField.get('fieldName', '').strip()  
                # Fetch the field value received from request and save the same in leadField.
                fieldValue = leadField['fieldValue'].strip() if leadField.get('fieldValue') else ''
                if modelLeadFieldsInfo.get(fieldName):                    
                    _leadField = modelLeadFieldsInfo[fieldName]
                    _leadField.fieldValue = fieldValue
                    _leadField.save()
                    log.info("UploadView:_saveLead, Lead field saved successfully, LeadField: [%s]" % _leadField)
                else:
                    # Check if the field is mapped
                    if fieldMappings.has_key(fieldName):
                        # Create new leadField as the leadField is not saved when master lead is created. 
                        _field = fieldMappings[fieldName]
                        _leadField = LeadFields(lead=leadMaster, field=_field, fieldValue=fieldValue)
                        _leadField.save()
                        modelLeadFieldsInfo[fieldName] = _leadField
                        log.info("UploadView:_saveLead, Created new LeadField: [%s] for field: [%s]" % (_leadField, fieldName))
                    else:
                        log.info("UploadView:_saveLead, LeadFields model does not have field: [%s]" % (fieldName))
                    
            # Save lead Details        
            # Get the lead associated with respective leadmaster and exhibitor booth
            leadModel = {} 
            leadDetailsModel = {}            
            if lead:
                log.info("UploadView:_saveLead, Lead exists, Lead: [%s]" % lead)
                # Lead already exists so need to update the records.
                leadModel['id'] = lead.id
                leadDetails = lead.leadDetails
                if leadDetails:
                    log.info("UploadView:_saveLead, LeadDetails exists, LeadDetails: [%s]" % leadDetails)
                    leadDetailsModel['id'] = leadDetails.id
                else:
                    log.info("UploadView:_saveLead, LeadDetails does not exists , new LeadDetails will be created.")
            else:
                log.info("UploadView:_saveLead, Lead does not exists, new Lead will be created.")

            # Validate the lead details fields, leadInfo also contains fields for LeadDetails
            leadInfo['device'] = device
            validationInfo = _validateFields(leadInfo, 'LeadDetails', isModel=True)
            statusCode, message, validatedLeadDetails = validationInfo
            if statusCode != 0:
                # Validation failed
                log.info("UploadView:_saveLead, LeadDetails validation failed.")
                return (statusCode, message, None)
            log.info("UploadView:_saveLead, LeadDetails validation successful, validatedLeadDetails: [%s]" % validatedLeadDetails)

            # Prepare the lead details model and save leadDetails                    
            leadDetailsModel['device'] = device
            leadDetailsModel['scanType'] = validatedLeadDetails['scanType']
            leadDetailsModel['syncID'] = validatedLeadDetails['syncID']        
            leadDetailsModel['leadSyncStatus'] = validatedLeadDetails['leadSyncStatus']
            leadDetailsModel['leadType'] = validatedLeadDetails['leadType']        
            leadDetailsModel['lookupStatus'] = validatedLeadDetails.get('lookupStatus', 'true')
            leadDetailsModel['captureTime'] = validatedLeadDetails['captureTime']
            
            log.info("UploadView:_saveLead, Saving LeadDetails, leadDetailsModel: [%s]" % leadDetailsModel)
            leadDetails = LeadDetails(**leadDetailsModel)
            leadDetails.save()
            log.info("UploadView:_saveLead, LeadDetails saved successfully, LeadDetails: [%s]" % leadDetails)
            
            # Save the lead
            leadModel['leadMaster'] = leadMaster
            leadModel['leadDetails'] = leadDetails
            leadModel['exhibitorBooth'] = exhibitorBooth                   
            log.info("UploadView:_saveLead, Saving Lead, leadModel: [%s]" % leadModel)
            lead = Lead(**leadModel)
            lead.save()
            log.info("UploadView:_saveLead, Lead saved successfully, Lead: [%s]" % lead)
            
            # Save the lead answers
            leadAnswers = leadInfo.get('leadAnswers', [])
            questionCount = 0
            for leadAnswer in leadAnswers:
                questionCount += 1
                # Check if qualifierQuestionID provided
                qualifierQuestionID = leadAnswer.get('qualifierQuestionID')
                if isinstance(qualifierQuestionID, basestring):
                    qualifierQuestionID = qualifierQuestionID.strip()                
                if not qualifierQuestionID:
                    log.info("UploadView:_saveLead, Question [%s], qualifierQuestionID not present." % questionCount)
                    continue
                # Check if qualifierQuestion exists
                qualifierQuestion = self._getObjectORNone(QualifierQuestions, id=qualifierQuestionID)
                if not qualifierQuestion:
                    _message = "QualifierQuestion object does not exists, qualifierQuestionID: [%s]" % qualifierQuestionID                    
                    log.info("UploadView:_saveLead, Question [%s], %s" % (questionCount, _message))
                    continue
                answerValue = leadAnswer['answerValue'] if leadAnswer.get('answerValue') else ''
                answerModel = dict()

                answer = self._getObjectORNone(Answer, lead=lead, question=qualifierQuestion)
                if answer:
                    log.info("UploadView:_saveLead, answer already exists, lead/question/answer: [%s]/[%s]/[%s]" % (lead, qualifierQuestion, answer))
                    answerModel['id'] = answer.id
                else:
                    log.info("UploadView:_saveLead, answer not exists, new entry will be created, lead/question: [%s]/[%s]" % (lead, qualifierQuestion))
                answerModel['lead'] = lead
                answerModel['question'] = qualifierQuestion
                answerModel['answer'] = answerValue
                answer = Answer(**answerModel)
                answer.save()
                log.info("UploadView:_saveLead, Question [%s], answer saved successfully, Answer: [%s]" % (questionCount, answer))
                        
            return (statusCode, message, lead)
        except Exception as ex:
            log.info("UploadView:_saveLead, Exception: [%s]" % str(ex))
            statusCode = errorCodes.SAVE_LEAD_EXCEPTION
            message = "Unable to save lead, Exception: [%s]" % str(ex)
            raise ex
            return (statusCode, message, None)           
            
    def _validateModelFields(self, modelName, modelFields):
        """
        """
        statusCode = 0
        msg = ''          
        validatedModelFields = modelFields.copy()
        try:
            timeFormat = settings.TRADESHOW_TIME_FORMAT
            # Get the predefined mapping for the model
            modelFieldMapping = modelFieldMappings[modelName]
            # Iterate through the modelFieldMapping and validate the fields
            for modelField in modelFieldMapping:
                fieldInfo = modelFieldMapping[modelField]
                modelFieldValue = modelFields.get(modelField)
                # Strip the empty spaces
                if isinstance(modelFieldValue, basestring):
                    modelFieldValue = modelFieldValue.strip()
                    validatedModelFields[modelField] = modelFieldValue
                # Validation for mandatory fields
                if fieldInfo.has_key('required') and fieldInfo['required']:
                    if modelFieldValue is None or modelFieldValue == '':
                        statusCode = errorCodes.FIELD_IS_MANDATORY
                        msg = "%s required for model %s" % (modelField, modelName)
                        raise ValueError(msg)    
                # Validation for datetime fields        
                if modelFieldValue:
                    if fieldInfo['type'] == 'datetime':
                        try:
                            datetimeObj = datetime.strptime(modelFieldValue, timeFormat)
                            validatedModelFields[modelField] = datetimeObj
                        except ValueError as ex:
                            statusCode = errorCodes.INVALID_DATETIME_VALUE
                            msg = "Invalid datetime value provided for Field: [%s], Value: [%s]" % (modelField, modelFieldValue)
                            raise ValueError(msg)    
                    elif fieldInfo['type'] == 'int':
                        try:
                            parsedModelFieldValue = int(modelFieldValue)
                            validatedModelFields[modelField] = parsedModelFieldValue
                        except ValueError as ex:
                            statusCode = errorCodes.INVALID_NUMERIC_VALUE
                            msg = "Invalid integer value provided for Field: [%s], Value: [%s]" % (modelField, modelFieldValue)
                            raise ValueError(msg)        
            # Validation successful                        
            return (statusCode, msg, validatedModelFields)
        except ValueError as ex:
            log.info("UploadView:_validateModelFields, ValueError Exception: [%s]" % str(ex))
        except Exception as ex:
            statusCode = errorCodes.VALIDATE_MODEL_FIELD_EXCEPTION            
            msg = "Got Exception in _validateModelFields, Exception: [%s]" % str(ex)
            
        return (statusCode, msg, modelFields)

    def _validateLeadsData(self, leadsData):
        """Validate the leads data.
        """
        log.info("UploadView:_validateLeadsData, leadsData: [%s]" % leadsData)
        statusCode = 0
        message = ''
        validationInfo = _validateFields(leadsData, 'LeadsData', isModel=False)
        statusCode, message, validatedLeadsData = validationInfo
        if statusCode != 0:
            log.info("UploadView:_validateLeadsData, leadsData validation failed.")
            return validationInfo            
        try:
            tradeshowID = validatedLeadsData['tradeshowID']
            exhibitorID = validatedLeadsData['exhibitorID']
            userName = validatedLeadsData['userName']
            # Validate tradeshow existance
            tradeshowObj = self._getObjectORNone(Tradeshow, id=tradeshowID)
            if not tradeshowObj:
                statusCode = errorCodes.TRADESHOW_NOT_EXISTS
                message = "Tradeshow does not exists, tradeshowID: [%s]" % tradeshowID
                raise ValueError(message)            
            # Validate exhibitor existence
            exhibitorObj = self._getObjectORNone(Exhibitor, id=exhibitorID)
            if not exhibitorObj:
                statusCode = errorCodes.EXHIBITOR_NOT_EXISTS
                message = "Exhibitor does not exists, exhibitorID: [%s]" % exhibitorID
                raise ValueError(message)
            # Validate exhibitor registration
            if exhibitorObj.tradeshow != tradeshowObj:
                statusCode = errorCodes.EXHIBITOR_NOT_REGISTERED
                message = "Exhibitor not registered under tradeshow, exhibitorName: [%s], tradeshowName: [%s]" % (exhibitorObj.name, tradeshowObj.name)
                raise ValueError(message)                            
            # Verify that userName is associated with exhibitor booth
            exhibitorBoothObj = self._getObjectORNone(ExhibitorBooth, exhibitor=exhibitorObj, userName__userName=userName)
            #exhibitorBoothObj = ExhibitorBooth.objects.get(exhibitor=exhibitorObj, userName__userName=userName)
            if not exhibitorBoothObj:
                statusCode = errorCodes.EXHIBITOR_BOOTH_NOT_EXISTS
                message = "UserName not registered under exhibitor, userName: [%s], exhibitorName: [%s]" % (userName, exhibitorObj.name)
                raise ValueError(message)
            # Update validated data
            validatedLeadsData['tradeshow'] = tradeshowObj
            validatedLeadsData['exhibitor'] = exhibitorObj
            validatedLeadsData['exhibitorBooth'] = exhibitorBoothObj
            # Validation successful
            return (statusCode, message, validatedLeadsData)
        except ValueError as ex:
            log.info("UploadView:_validateLeadsData, ValueError Exception: [%s]" % str(ex))
        except Exception as ex:
            statusCode = errorCodes.VALIDATE_LEADS_DATA_EXCEPTION
            message = "Got Exception in _validateLeadsData, Exception: [%s]" % str(ex)
            log.info("UploadView:_validateLeadsData, Exception: [%s]" % str(ex))
        # Validation failed
        return (statusCode, message, [])
                
    def _getObjectORNone(self, model, *args, **kwargs):
        modelName = model.__name__
        try:
            log.info("In _getObjectORNone, Model: [%s] , args: [%s], kwargs: [%s]" % (modelName, args, kwargs))
            modelObj = model.objects.get(*args, **kwargs)
            log.info("In _getObjectORNone, Model [%s], object exists, [%s]" % (modelName, modelObj))
            return modelObj
        except model.DoesNotExist:
            log.info("In _getObjectORNone, Model [%s], object does not exists." % modelName)
            return None
            
def _getDefaultresponse():
    """
    """
    response = dict()
    response['response'] = {}
    response['responseHeader'] = {'status': 0}
    return response
    
    

def _validateFields(fields, fieldsKey, isModel=False):
    """Validate the fields.
    """
    booleanMapping = {'true': True, 'false': False, '1': True, '0': False}
    booleanValues = set(['true', 'false', '1', '0'])
    statusCode = 0
    message = ''
    validatedFields = fields.copy()
    try:
        timeFormat = settings.TRADESHOW_TIME_FORMAT
        # Get the predefined mapping for fields
        if isModel:
            fieldMapping = modelFieldMappings.get(fieldsKey)
        else:
            fieldMapping = validationFieldMappings.get(fieldsKey)            
        if not fieldMapping:
            statusCode = errorCodes.FIELD_MAPPING_NOT_AVAILABLE
            message = 'No field mapping available for %s fields' % fieldsKey
            return (statusCode, message, {})
                    
        # Iterate through the fieldMapping and validate the fields
        for field in fieldMapping:
            fieldInfo = fieldMapping[field]
            fieldValue = fields.get(field)
            # Strip the empty spaces
            if isinstance(fieldValue, basestring):
                fieldValue = fieldValue.strip()
                validatedFields[field] = fieldValue
            # Validation for mandatory fields
            if fieldInfo.has_key('required') and fieldInfo['required']:
                if fieldValue is None or fieldValue == '':
                    statusCode = errorCodes.FIELD_IS_MANDATORY
                    message = "%s is required for %s" % (field, fieldsKey)
                    raise ValueError(message)
            # Validation for typed fields like, datetime, integer, boolean
            # TODO: Handle fields which are not mandatory and has type other that text
            if fieldValue:
                if fieldInfo['type'] == 'datetime':
                    try:
                        datetimeObj = datetime.strptime(fieldValue, timeFormat)
                        validatedFields[field] = datetimeObj
                    except ValueError as ex:
                        statusCode = errorCodes.INVALID_DATETIME_VALUE
                        message = "Invalid datetime value provided for Field: %s, Value: %s" % (field, fieldValue)
                        raise ValueError(message)
                elif fieldInfo['type'] == 'integer':
                    try:
                        parsedFieldValue = int(fieldValue)
                        validatedFields[field] = parsedFieldValue
                    except ValueError as ex:
                        statusCode = errorCodes.INVALID_NUMERIC_VALUE
                        message = "Invalid integer value provided for Field: %s, Value: %s" % (field, fieldValue)
                        raise ValueError(message)
                elif fieldInfo['type'] == 'boolean':
                    isValid = False
                    if isinstance(fieldValue, bool):
                        validatedFields[field] = fieldValue
                        isValid = True
                    elif isinstance(fieldValue, basestring):
                        if fieldValue in booleanValues:
                            validatedFields[field] = booleanMapping[fieldValue]
                            isValid = True                        
                    if not isValid:
                        statusCode = errorCodes.INVALID_BOOLEAN_VALUE
                        message = "Invalid boolean value provided for Field: %s, Value: %s" % (field, fieldValue)
                        raise ValueError(message)                        
        # Validation successful                        
        return (statusCode, message, validatedFields)
    except ValueError as ex:
        log.info("UploadView:_validateFields, ValueError Exception: [%s]" % str(ex))
    except Exception as ex:
        log.info("UploadView:_validateFields, Exception: [%s]" % str(ex))
        statusCode = errorCodes.VALIDATE_MODEL_FIELD_EXCEPTION            
        message = "Got Exception in _validateFields, Exception: [%s]" % str(ex)        
    # Validation failed
    return (statusCode, message, {})
