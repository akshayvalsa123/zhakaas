import logging
import json
from datetime import datetime

from django.views.generic import View
from django.http import JsonResponse
from django.db import transaction

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from tradeshow.common import error_codes as errorCodes
from tradeshow.common import model_apis as modelAPIs
from tradeshow.common.utils import _buildResponse
from tradeshow.common.exceptions import SyncException
from tradeshow.common.field_mappings import modelFieldMappings, validationFieldMappings

from api.models import UserLogin
from api.models import UserLoginSession
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

class SyncView(View):
    """View for sync.
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
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(SyncView, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        """
        """
        response = _buildResponse(errorCodes.LEAD_SYNC_GET_METHOD_NOT_ALLOWED, "GET method not allowed")
        return JsonResponse(response)
            
    def post(self, request):
        """Handles lead sync request.
        """
        try:
            response = dict()
            _authToken = ''
            leadsData = json.loads(request.body)		
	    log.info("leadsData: [%s]" % leadsData)
            # Get current user auth token
            username = leadsData.get('userName', '').strip()
            _authToken = _getUserAuthToken(username)
            # Authenticate the request
            authInfo = self._authenticateRequest(request, leadsData)
            log.info("SyncView:post, authInfo: [%s]" % (authInfo,))
            statusCode, message, authData = authInfo
            if statusCode != 0: # Validation failed, return the error response.            
                raise SyncException(statusCode, message)

		    # Validate leads data
            validationInfo = self._validateLeadsData(leadsData)
            log.info("SyncView:post, validationInfo: [%s]" % (validationInfo,))
            statusCode, message, validatedLeadsData = validationInfo
            if statusCode != 0: # Validation failed, return the error response.            
                raise SyncException(statusCode, message)
                
            # TODO: Disabling the device save , need to enble later.
            device = None
            if False:    
                # Save device details
                deviceDetails = validatedLeadsData['deviceDetails']
                log.info("SyncView:post, deviceDetails: [%s]" % (deviceDetails))
                saveDeviceInfo = self._saveDevice(deviceDetails)
                log.info("SyncView:post, saveDeviceInfo: [%s]" % (saveDeviceInfo,))
                statusCode, message, device = saveDeviceInfo
                if statusCode != 0: # Validation failed, return the error response.            
                    raise SyncException(statusCode, message)
                        
            # Save leads
            exhibitorBooth = validatedLeadsData['exhibitorBooth']
            tradeshow = validatedLeadsData['tradeshow']
            leads = validatedLeadsData['leads']
            log.info("SyncView:post, tradeshow/exhibitorBooth/leadsCount: [%s/%s/%s]" % (tradeshow, exhibitorBooth, len(leads)))
            count = 0
            failedCount = 0
            savedLeads = []
            for lead in leads:
                count += 1
                # Save lead
                leadID = lead.get('leadID')
                log.info("SyncView:post,==================== Start Saving Lead [%s], leadID [%s] ====================" % (count, leadID))
                saveLeadInfo = self._saveLead(lead, device, exhibitorBooth, tradeshow)
                log.info("SyncView:post, saveLeadInfo: [%s]" % (saveLeadInfo,))
                statusCode, message, _lead = saveLeadInfo
                if statusCode != 0:
                    log.info("SyncView:post, Lead save failed, will continue for next available lead.")
                    failedCount += 1
                else:
                    log.info("SyncView:post, Lead save successful, Lead: [%s]" % _lead)
                    savedLeads.append(leadID)
                log.info("SyncView:post,==================== End Saving Lead [%s], leadID [%s] ====================" % (count, leadID))
                # Process lead fields
            log.info("SyncView:post, Total leads processed: [%s], Failed Leads: [%s]" % (count, failedCount))            
            syncInfo = dict()
            syncInfo['savedLeadsCount'] = len(savedLeads)
            syncInfo['savedLeads'] = savedLeads
            syncInfo['totalLeadsCount'] = count
            syncInfo['failedLeadsCount'] = failedCount
            syncInfo['authToken'] = _authToken
            response = _buildResponse(0, '', moreInfo=syncInfo)
            return JsonResponse(response)
        except SyncException as ex:
            log.info("SyncView:post, SyncException, statusCode: [%s], message: [%s]" % (ex.statusCode, ex.message))           
            response = _buildResponse(ex.statusCode, ex.message, moreInfo={'authToken': _authToken})
        except Exception as ex:
            log.info("SyncView:post, Exception: [%s]" % str(ex))           
            response = _buildResponse(errorCodes.SYNC_VIEW_EXCEPTION, "Unable to sync leads.", moreInfo={'authToken': _authToken})
        return JsonResponse(response)

    def _saveDevice(self, deviceDetails):
        """Add/Update the device.
        """        
        device = None
        log.info("SyncView:_saveDevice, deviceDetails: [%s]" % deviceDetails)
        try:
            with transaction.atomic():
                validationInfo = _validateFields(deviceDetails, 'DeviceDetails', isModel=True)
                statusCode, message, validatedDeviceDetails = validationInfo
                log.info("SyncView:_saveDevice, statusCode/message/validatedDeviceDetails :[%s/%s/%s]" % (statusCode, message, validatedDeviceDetails ))
                if statusCode != 0:
                    log.info("SyncView:_saveDevice, DeviceDetails validation failed.")
                    raise SyncException(statusCode, message)
                log.info("SyncView:_saveDevice, DeviceDetails validation successful.")            
                # TODO: Need to check if device already exists for the lead details            
                deviceID = deviceDetails['deviceID']
                device = modelAPIs._getObjectORNone(DeviceDetails, deviceID=deviceID)
                log.info("SyncView:_saveDevice, device: [%s]" % device)            
                if device:
                    log.info("SyncView:_saveDevice, Device already exists, updating the device infromation.")
                    # Set the id field such that save will update the record.
                    validatedDeviceDetails['id'] = device.id
                else:
                    log.info("SyncView:_saveDevice, Device does not exists, creating the device infromation.")
                log.info("SyncView:_saveDevice, Saving DeviceDetails")
                device = DeviceDetails(**validatedDeviceDetails)
                device.save()
                log.info("SyncView:_saveDevice, Device saved successfully, ID/deviceID: [%s]/[%s]" % (device.id, device.deviceID))
                response = (statusCode, message, device)
        except SyncException as ex:
            log.info("SyncView:_saveDevice, SyncException, statusCode: [%s], message: [%s]" % (ex.statusCode, ex.message))           
            response = (ex.statusCode, ex.message, device)
        except Exception as ex:
            log.info("SyncView:_saveDevice, Exception: [%s]" % str(ex))           
            response = (errorCodes.SAVE_DEVICE_EXCEPTION, "Unable to sync leads.")
        return response

    def _saveLead(self, leadInfo, device, exhibitorBooth, tradeshow):
        """Add/update the lead.
        """     
        statusCode = 0
        message = ''   
        log.info("SyncView:_saveLead, leadInfo: [%s], device: [%s], exhibitorBooth: [%s], tradeshow: [%s]" % (leadInfo, device, exhibitorBooth, tradeshow))
        try:
            with transaction.atomic():
                timeFormat = settings.TRADESHOW_TIME_FORMAT
                modelLeadFieldsInfo = dict()
                # Get the lead master and lead
                leadID = leadInfo.get('leadID')
                log.info("SyncView:_saveLead, leadID: [%s]" % leadID)
                leadMaster = modelAPIs._getObjectORNone(LeadMaster, leadID=leadID, tradeshow=tradeshow)        
                log.info("SyncView:_saveLead, leadMaster: [%s]" % leadMaster)
                if leadMaster:
                    log.info("SyncView:_saveLead, leadMaster exists, leadID: [%s]" % leadID)
                    # Fetch the lead fields associated with leadMaster and prepare mapping
                    modelLeadFields = LeadFields.objects.filter(lead=leadMaster)                
                    for modelLeadField in modelLeadFields:
                        modelLeadFieldsInfo[modelLeadField.field.name] = modelLeadField
                    log.info("SyncView:_saveLead, modelLeadFieldsInfo: [%s]" % modelLeadFieldsInfo)
                    # Get the lead associated with lead master
                    lead = modelAPIs._getObjectORNone(Lead, leadMaster=leadMaster, exhibitorBooth=exhibitorBooth)
                    log.info("SyncView:_saveLead, Associated lead: [%s]" % lead)
                else:
                    log.info("SyncView:_saveLead, leadMaster does not exists, new lead will be created. leadID: [%s]" % leadID)
                    leadMaster = LeadMaster(leadID=leadID, tradeshow=tradeshow)
                    leadMaster.save()
                    log.info("SyncView:_saveLead, Created new leadMaster: [%s]" % leadMaster)
                    lead = None
                    
                # Get the tradeshow fields mapping
                tradeshowMapping = tradeshow.mapping_set.get()
                _fieldMappings = FieldsMapping.objects.filter(mapping=tradeshowMapping).order_by('fieldSeq')
                fieldMappings = dict()
                for _fieldMapping in _fieldMappings:
                    fieldMappings[_fieldMapping.field.name] = _fieldMapping.field
                log.info("SyncView:_saveLead, fieldMappings: [%s]" % fieldMappings)
                # Save the lead fields 
                leadFields = leadInfo.get('leadFields', [])
                log.info("SyncView:_saveLead, leadFields: [%s]" % leadFields)
                for leadField in leadFields:
                    # Fetch the field name received from request
                    fieldName = leadField.get('fieldName', '').strip()  
                    # Fetch the field value received from request and save the same in leadField.
                    fieldValue = leadField['fieldValue'].strip() if leadField.get('fieldValue') else ''
                    if modelLeadFieldsInfo.get(fieldName):                    
                        _leadField = modelLeadFieldsInfo[fieldName]
                        _leadField.fieldValue = fieldValue
                        _leadField.save()
                        log.info("SyncView:_saveLead, Lead field saved successfully, LeadField: [%s]" % _leadField)
                    else:
                        # Check if the field is mapped
                        if fieldMappings.has_key(fieldName):
                            # Create new leadField as the leadField is not saved when master lead is created. 
                            _field = fieldMappings[fieldName]
                            _leadField = LeadFields(lead=leadMaster, field=_field, fieldValue=fieldValue)
                            _leadField.save()
                            modelLeadFieldsInfo[fieldName] = _leadField
                            log.info("SyncView:_saveLead, Created new LeadField: [%s] for field: [%s]" % (_leadField, fieldName))
                        else:
                            log.info("SyncView:_saveLead, LeadFields model does not have field: [%s]" % (fieldName))
                       
                # Save lead Details        
                # Get the lead associated with respective leadmaster and exhibitor booth
                leadModel = {} 
                leadDetailsModel = {}            
                if lead:
                    log.info("SyncView:_saveLead, Lead exists, Lead: [%s]" % lead)
                    # Lead already exists so need to update the records.
                    leadModel['id'] = lead.id
                    leadDetails = lead.leadDetails
                    log.info("SyncView:_saveLead, leadDetails: [%s]" % leadDetails)
                    if leadDetails:
                        log.info("SyncView:_saveLead, LeadDetails exists")
                        leadDetailsModel['id'] = leadDetails.id
                    else:
                        log.info("SyncView:_saveLead, LeadDetails does not exists , new LeadDetails will be created.")
                else:
                    log.info("SyncView:_saveLead, Lead does not exists, new Lead will be created.")

                # Validate the lead details fields, leadInfo also contains fields for LeadDetails
                leadInfo['device'] = device
                validationInfo = _validateFields(leadInfo, 'LeadDetails', isModel=True)
                statusCode, message, validatedLeadDetails = validationInfo
                log.info("SyncView:_saveLead, statusCode/message/validatedLeadDetails: [%s/%s/%s]" % (statusCode, message, validatedLeadDetails))            
                if statusCode != 0:
                    # Validation failed
                    log.info("SyncView:_saveLead, LeadDetails validation failed.")
                    raise SyncException(statusCode, message)
                log.info("SyncView:_saveLead, LeadDetails validation successful")

                # Prepare the lead details model and save leadDetails                    
                #leadDetailsModel['device'] = device
                leadDetailsModel['scanType'] = validatedLeadDetails['scanType']
                leadDetailsModel['syncID'] = validatedLeadDetails['syncID']        
                leadDetailsModel['leadSyncStatus'] = validatedLeadDetails['leadSyncStatus']
                leadDetailsModel['leadType'] = validatedLeadDetails['leadType']        
                leadDetailsModel['lookupStatus'] = validatedLeadDetails.get('lookupStatus', 'true')
                leadDetailsModel['captureTime'] = validatedLeadDetails['captureTime']
                if validatedLeadDetails.get('rating'):
                    leadDetailsModel['rating'] = validatedLeadDetails['rating']
                if validatedLeadDetails.get('comment'):
                    leadDetailsModel['comment'] = validatedLeadDetails['comment']
                log.info("SyncView:_saveLead, Saving LeadDetails, leadDetailsModel: [%s]" % leadDetailsModel)
                leadDetails = LeadDetails(**leadDetailsModel)
                leadDetails.save()
                log.info("SyncView:_saveLead, LeadDetails saved successfully, LeadDetails: [%s]" % leadDetails)
                
                # Save the lead
                leadModel['leadMaster'] = leadMaster
                leadModel['leadDetails'] = leadDetails
                leadModel['exhibitorBooth'] = exhibitorBooth                   
                log.info("SyncView:_saveLead, Saving Lead, leadModel: [%s]" % leadModel)
                lead = Lead(**leadModel)
                lead.save()
                log.info("SyncView:_saveLead, Lead saved successfully, Lead: [%s]" % lead)
                
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
                        log.info("SyncView:_saveLead, Question [%s], qualifierQuestionID not present." % questionCount)
                        continue
                    # Check if qualifierQuestion exists
                    qualifierQuestion = self._getObjectORNone(QualifierQuestions, id=qualifierQuestionID)
                    if not qualifierQuestion:
                        _message = "SyncView:_saveLead, QualifierQuestion object does not exists, qualifierQuestionID: [%s]" % qualifierQuestionID                    
                        log.info("SyncView:_saveLead, Question [%s], %s" % (questionCount, _message))
                        continue
                    answerValue = leadAnswer['answerValue'] if leadAnswer.get('answerValue') else ''
                    answerModel = dict()

                    answer = self._getObjectORNone(Answer, lead=lead, question=qualifierQuestion)
                    if answer:
                        log.info("SyncView:_saveLead, answer already exists, lead/question/answer: [%s]/[%s]/[%s]" % (lead, qualifierQuestion, answer))
                        answerModel['id'] = answer.id
                    else:
                        log.info("SyncView:_saveLead, answer not exists, new entry will be created, lead/question: [%s]/[%s]" % (lead, qualifierQuestion))
                    answerModel['lead'] = lead
                    answerModel['question'] = qualifierQuestion
                    answerModel['answer'] = answerValue
                    answer = Answer(**answerModel)
                    answer.save()
                    log.info("SyncView:_saveLead, Question [%s], answer saved successfully, Answer: [%s]" % (questionCount, answer))

                response = (statusCode, message, lead)
        except SyncException as ex:
            log.info("SyncView:_saveLead, SyncException, statusCode: [%s], message: [%s]" % (ex.statusCode, ex.message))           
            response = (ex.statusCode, ex.message, None)
        except Exception as ex:
            log.info("SyncView:_saveLead, Exception: [%s]" % str(ex))           
            response = (errorCodes.SAVE_LEAD_EXCEPTION, "Unable to save lead.", None)
        return response

            
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
            log.info("SyncView:_validateModelFields, ValueError Exception: [%s]" % str(ex))
        except Exception as ex:
            statusCode = errorCodes.VALIDATE_MODEL_FIELD_EXCEPTION            
            msg = "Got Exception in _validateModelFields, Exception: [%s]" % str(ex)
            
        return (statusCode, msg, modelFields)

    def _validateLeadsData(self, leadsData):
        """Validate the leads data.
        """
        log.info("SyncView:_validateLeadsData, leadsData: [%s]" % leadsData)
        statusCode = 0
        message = ''
        validationInfo = _validateFields(leadsData, 'LeadsData', isModel=False)
        statusCode, message, validatedLeadsData = validationInfo
        if statusCode != 0:
            log.info("SyncView:_validateLeadsData, leadsData validation failed.")
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
            log.info("SyncView:_validateLeadsData, ValueError Exception: [%s]" % str(ex))
        except Exception as ex:
            statusCode = errorCodes.VALIDATE_LEADS_DATA_EXCEPTION
            message = "Got Exception in _validateLeadsData, Exception: [%s]" % str(ex)
            log.info("SyncView:_validateLeadsData, Exception: [%s]" % str(ex))
        # Validation failed
        return (statusCode, message, [])

    def _authenticateRequest(self, request, leadsData):
        """Authenticate request.
        """
        log.info("SyncView:_authenticateRequest, leadsData: [%s]" % leadsData)
        statusCode = 0
        message = ''

        try:
            username = leadsData.get('userName', '').strip()
            #authToken = leadsData.get('authToken', '').strip()
            authToken = request.META.get('HTTP_X_AUTH_TOKEN', '').strip()
            log.info("SyncView:_authenticateRequest, username/authToken: [%s/%s]" % (username, authToken))
            if not (username and authToken):
                message = "Invalid request, username/authtoken not provided."
                raise ValueError(message)

            # Validate User Login
            userLogin = self._getObjectORNone(UserLogin, userName=username)
            log.info("SyncView:_authenticateRequest, UserLogin: [%s]" % userLogin)
            if not userLogin:
                log.info("SyncView:_authenticateRequest, Invalid user provided.")
                message = "Invalid request, user not exists."                
                raise ValueError(message)

            # Get the users last login session
            userLoginSession = self._getObjectORNone(UserLoginSession, user=userLogin, authToken=authToken)
            if not userLoginSession:
                message = "Invalid request, user not logged in."
                log.info("SyncView:_authenticateRequest, User not logged in.")
                raise ValueError(message)
            # User is logged out, still we are saving the remaining leads.
            if userLoginSession.logoutTime:
                message = "Invalid request, user logged out."
                log.info("SyncView:_authenticateRequest, user logged out.")
                #raise ValueError(message)
            return (0, '', [])
        except ValueError as ex:
            log.info("SyncView:_authenticateRequest, ValueError Exception: [%s]" % str(ex))
            return (-1, message, [])
        except Exception as ex:
            statusCode = errorCodes.AUTHENTICATE_REQUEST_EXCEPTION
            message = "Got Exception in _authenticateRequest, Exception: [%s]" % str(ex)
            log.info("SyncView:_authenticateRequest, Exception: [%s]" % str(ex))        
            return (-1, message, [])
                
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
        log.info("SyncView:_validateFields, ValueError Exception: [%s]" % str(ex))
    except Exception as ex:
        log.info("SyncView:_validateFields, Exception: [%s]" % str(ex))
        statusCode = errorCodes.VALIDATE_MODEL_FIELD_EXCEPTION            
        message = "Got Exception in _validateFields, Exception: [%s]" % str(ex)        
    # Validation failed
    return (statusCode, message, {})

def _getUserAuthToken(username):
    """Return the current auth token for the user.
    """
    try:
        user = modelAPIs._getObjectORNone(UserLogin, userName=username)
        log.info("SyncView:_getUserAuthToken: user: [%s]" % user)
        sessions = UserLoginSession.objects.filter(user=user).order_by('-loginTime')
        log.info("SyncView:_getUserAuthToken: sessions: [%s]" % sessions)
        if sessions:
            lastSession = sessions[0]
            log.info("_getUserAuthToken: lastSession: [%s]" % lastSession)
            return lastSession.authToken
        log.info("SyncView:_getUserAuthToken, User does not have any sessions.")
        return ''
    except Exception as ex:
        log.info("SyncView:_getUserAuthToken, Exception: [%s]" % str(ex))
        return ''

