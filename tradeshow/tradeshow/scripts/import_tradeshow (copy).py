import os
import json
import logging 
import traceback
from datetime import datetime
from django.conf import settings
from django.db import transaction

from api.field_mappings import modelFieldMappings, validationFieldMappings
from api import error_codes as errorCodes
from api.models import Address
from api.models import Fields
from api.models import UserLogin
from api.models import Exhibitor
from api.models import ExhibitorBooth
from api.models import Tradeshow
from api.models import FieldsMapping
from api.models import Mapping
from api.models import TradeshowSettings
from api.models import Qualifier
from api.models import QualifierType
from api.models import Question
from api.models import QualifierQuestions
from api.models import DeviceDetails
from api.models import LeadMaster
from api.models import Lead
from api.models import LeadDetails
from api.models import LeadFields
from api.models import Answer
from api.models import Settings

# Initialise Logger
log = logging.getLogger(__name__)
hdlr = logging.StreamHandler()
#hdlr = logging.FileHandler('/tmp/import_ts.log')
#hdlr = logging.handlers.RotatingFileHandler('/tmp/logs/add_artifact_creatorID.log', maxBytes=10*1024*1024, backupCount=500)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
log.addHandler(hdlr)
log.setLevel(logging.INFO)


tradeshowFile = "/home/akshay/Desktop/sync/Register_TS_FK_V2.xlsx"
widgets = set(['EditText', 'Checkbox', 'Spinner'])
modelNames = ['Address', 'Tradeshow', 'Mapping', 'Fields', 'Exhibitor', 'Qualifier', 'Questions', 'Settings']
modelColumns = dict()
modelColumns['Address'] =  ['address1', 'address2', 'street', 'city', 'state', 'country', 'zipcode', 'name']
modelColumns['Tradeshow'] = ['name', 'nameCode', 'startDate', 'endDate', 'email', 'contactNo', 'adminPassword', 'supportMessage', 'website', 'timeZone', 'oldName']
modelColumns['Mapping'] = ['totalFields', 'badgeIDFieldSeq', 'badgeDataFieldSeq']
modelColumns['Fields'] = ['name', 'displayName', 'description', 'fieldSeq']
modelColumns['Exhibitor'] = ['name', 'email', 'contactNo', 'alternateEmail', 'alternateContactNo', 'licenseCount', 'userName', 'password']
modelColumns['Qualifier'] = ['qualifierType', 'qualifierName', 'screenNo', 'ansFormat', 'totalQuestions']
modelColumns['Questions'] = ['qualifierName', 'question', 'widgetName', 'options', 'questionSeq']
modelColumns['Settings'] = ['settingType', 'settingName', 'settingValue', 'defaultSettingValue']


class ImportTradeshow(object):
    """Class to handle import tradeshow.
    """

    def __init__(self):
        """
        """        
        self.modelNames = set(['Address', 'Tradeshow', 'Mapping', 'Fields', 'Exhibitor', 'Qualifier', 'Questions', 'Settings'])
        self.modelColumns = dict()
        self.modelColumns['Address'] =  ['address1', 'address2', 'street', 'city', 'state', 'country', 'zipcode', 'name']
        self.modelColumns['Tradeshow'] = ['name', 'nameCode', 'startDate', 'endDate', 'email', 'contactNo', 'adminPassword', 'supportMessage', 'website', 'timeZone', 'oldName']
        self.modelColumns['Mapping'] = ['totalFields', 'badgeIDFieldSeq', 'badgeDataFieldSeq']
        self.modelColumns['Fields'] = ['name', 'displayName', 'description', 'fieldSeq']
        self.modelColumns['Exhibitor'] = ['name', 'email', 'contactNo', 'alternateEmail', 'alternateContactNo', 'licenseCount', 'userName', 'password']
        self.modelColumns['Qualifier'] = ['qualifierType', 'qualifierName', 'screenNo', 'ansFormat', 'totalQuestions']
        self.modelColumns['Questions'] = ['qualifierName', 'question', 'widgetName', 'options', 'questionSeq']
        self.modelColumns['Settings'] = ['settingType', 'settingName', 'settingValue', 'defaultSettingValue']
        self.widgets = set(['EditText', 'Checkbox', 'Spinner'])
        self.response = dict()
        self.response['response'] = {}
        self.response['responseHeader'] = {'status': 0}

    def importFromFile(tradeshowFile)
        """Import the tradeshow from XLSX file
        """
        # Check if the tradeshow file exists.
        if not os.path.exists(tradeshowFile):
            log.info("ImportTradeshow:importFromFile, Tradeshow import failed, File [%s] does not exists.." % tradeshowFile)
            message = "Tradeshow import failed, File does not exists."
            return self._sendResponse(errorCodes.FILE_DOES_NOT_EXISTS, message)
        # Build the josn from tradeshow file
        statusCode, message, tradeshowJson = self._getTradeshowJson(tradeshowFile)
        log.info("statusCode: [%s], message: [%s], tradeshowJson:[%s]" %(statusCode, message, tradeshowJson))
        if statusCode != 0:            
            log.info("ImportTradeshow:importFromFile, unable to get tradeshow json.")
            message = "ImportTradeshow:importFromFile, unable to get tradeshow json"
            return self._sendResponse(statusCode, message)
        # Verify if any models information is missing.
        _modelNames = set(tradeshowJson.keys())
        missingModels = self.modelNames - _modelNames
        if missingModels:
            log.info("ImportTradeshow:importFromFile, Not all models information provided.Missing models: [%s]" % missingModels)            
            statusCode = errorCodes.IMPORT_MODEL_MISSING
            message = "Missing models information."            
            return self._sendResponse(statusCode, message)

    def _sendResponse(self, statusCode, message):
        """
        """
        self.response['response'] = {'message': message}
        self.response['responseHeader']['status'] = statusCode
        return self.response

def main():
    """  
    """
    response = {}
    modelFields = {}
    statusCode, message, tradeshowJson = _getTradeshowJson(tradeshowFile)
    log.info("statusCode: [%s], message: [%s], tradeshowJson:[%s]" %(statusCode, message, tradeshowJson))
    if statusCode != 0:
        log.info("Main::_getTradeshowJson Failed.")
        return
    _modelNames = models_json.keys()
    missing_models = set(modelNames) - set(_modelNames)
    if missing_models:
        log.info("Not all models provided. Missing models: [%s]" % missing_models)
        return
    record_count = 0    
    for model_name in models_json:
        model_records = models_json[model_name]
        for model_record in model_records:
            record_count += 1
            result = _validateFields(model_record, model_name, isModel=True)
            status_code, message, validated_fields = result
            if status_code != 0:
                raise Exception(message)
            model_fields.setdefault(model_name, []).append(validated_fields)
    if not record_count:
        log.info("Empty file no records available.")
        return
    log.info("Field validation completed")
    try:
        result = _delete_existing_tradeshow(model_fields)
        log.info("Delete existing, Result: [%s]" % (result,))
        if not result[0]:
            return result[1]
    except Exception as ex:
        log.info("Got exception from _delete_existing_tradeshow, Error:[%s]" % str(ex))
        raise ex
    result = _validateModels(model_fields)
    statusCode, message = result
    if statusCode != 0:
        return
    _save_tardeshow(model_fields)
    #print validated_models

def _delete_existing_tradeshow(model_fields):
    """
    """
    tradeshow = model_fields['Tradeshow'][0]
    # Get the tradehsow address
    tradeshowName = tradeshow['oldName']
    with transaction.atomic():
        tradeshowObj = _getObjectORNone(Tradeshow, name=tradeshowName)
        # If tradeshow does not exists return
        if not tradeshowObj:
            log.info("Tradeshow does not exists, Name: [%s]" % tradeshowName)
            return (True, "")
        # If tradeshow exists so delete the same
        log.info("Tradeshow exists, Name/ID: [%s/%s]" % (tradeshowName, tradeshowObj.id))
        leadCount = LeadMaster.objects.filter(tradeshow=tradeshowObj).count()
        if leadCount:
            return (False, "Tradeshow has leads, cannot update/delete tradeshow.")
            
        # Get tradeshow address
        tradeshowAddress = tradeshowObj.address
        # Get exhibitor addresses
        exhibitors = Exhibitor.objects.filter(tradeshow=tradeshowObj)
        exhibitorAddresses = [exhibitor.address for exhibitor in exhibitors]
        # Get user logins
        exhibitorBooths = ExhibitorBooth.objects.filter(exhibitor__in=exhibitors)
        userLogins = [exhibitorBooth.userName for exhibitorBooth in exhibitorBooths]
        # Get the questions
        qualifiers = Qualifier.objects.filter(exhibitor__in=exhibitors)
        questions = []
        # Fetch questions from each qualifier
        for qualifier in qualifiers:
            _questions = qualifier.questions.all()
            questions.extend(_questions)
        # Two qualifiers can have same questions so filter out duplicate questions.
        questions = list(set(questions))
        # Delete tradeshow address
        log.info("Deleting tradeshowAddress: [%s]" % tradeshowAddress)
        tradeshowAddress.delete()
        # Delete exhibitor addresses    
        log.info("Deleting exhibitorAddresses: [%s]" % exhibitorAddresses)
        for exhibitorAddress in exhibitorAddresses:
            exhibitorAddress.delete()
        # Delete userLogins
        log.info("Deleting userLogins: [%s]" % userLogins)
        for userLogin in userLogins:
            userLogin.delete()
        # Delete questions
        log.info("Deleting questions: [%s]" % questions)
        for question in questions:
            question.delete()
        # Delete Tradeshow, this will do a cascade delete and hence will also delete below records
        # Mappings, Exhibitors, Exhibitor booths, Fields mappings, Qualifiers, Qualifier questionss
        tradeshowObj.delete()
    return (True, "")

def _save_tardeshow(model_fields, update):
    """Save the tradeshow.
       Steps ::
                If create tradeshow :
                    # Add all addresses
                    # Add tradeshow (Check if tradeshow already exists)
                    # Add mapping
                    # Add fields (Check if field with same name already exists)
                    # Add Field Mappings
                    # Add exhibitor
                    # Create username , based on licence count
                    # Create exhibitor booths
                    # Create qualifier type if not exists
                    # Create qualifier
                    # Create questions
                    # Create QualifierQuestions
                    # Create settigs if not exists
                    # Create Tradeshow settings    
    """
    with transaction.atomic():
        addressModels = {}
        # Save address object for tradeshow and exhibitors
        addressList = model_fields['Address']
        for address in addressList:
            # Get the name for which address is to be built
            name = address['name']
            del address['name']
            # Save the address
            _address = Address(**address)
            _address.save()
            addressModels[name] = _address
        # Save tradeshow
        tradeshow = model_fields['Tradeshow'][0]
        # Get the tradehsow address
        tradeshowName = tradeshow['name']    
        tradeshowObj = _getObjectORNone(Tradeshow, name=tradeshowName)
        if update:
            pass
        else:
            # Create new tradeshow
            if tradeshowObj:
                raise Exception("Tradeshow already exists.")
        tradeshow['address'] = addressModels[tradeshowName]
        if tradeshow.has_key('oldName'):
            oldName = tradeshow['oldName']
            del tradeshow['oldName']
        _tradeshow = Tradeshow(**tradeshow)
        _tradeshow.save()
        # Save Mapping
        mapping = model_fields['Mapping'][0]
        mapping['tradeshow'] = _tradeshow
        _mapping = Mapping(**mapping)
        _mapping.save()
        # Save field and fieldsMapping
        fields = model_fields['Fields']
        for field in fields:
            fieldSeq = field['fieldSeq']
            del field['fieldSeq']
            # Save field if not already exists
            _field = _getObjectORNone(Fields, name=field['name'])
            if not _field:
                _field = Fields(**field)
                _field.save()
            # Save fieldsMapping
            fieldsMapping = dict()
            fieldsMapping['mapping'] = _mapping
            fieldsMapping['field'] = _field
            fieldsMapping['fieldSeq'] = fieldSeq
            fieldsMapping['isUnique'] = False
            _fieldsMapping = FieldsMapping(**fieldsMapping)
            _fieldsMapping.save()
        # Save Exhibitor
        exhibitors = model_fields['Exhibitor']
        exhibitorModels = dict()
        for exhibitor in exhibitors:
            name = exhibitor['name']
            userName = exhibitor['userName']
            password = exhibitor['password']
            licenseCount = exhibitor['licenseCount']
            del exhibitor['userName']
            del exhibitor['password']
            exhibitor['tradeshow'] = _tradeshow
            exhibitor['address'] = addressModels[name]
            _exhibitor = Exhibitor(**exhibitor)
            _exhibitor.save()
            exhibitorModels[name] = _exhibitor
            for index in range(licenseCount):
                boothNo  = str(index + 1).zfill(3)
                updatedUserName = "%s%s" % (userName, boothNo)
                # Save user login
                userLogin = {}
                userLogin['userName'] = updatedUserName
                userLogin['password'] = password
                userLogin['isActive'] = True
                _userLogin = UserLogin(**userLogin)
                _userLogin.save()
                # Save exhibitorBooth
                exhibitorBooth = dict()
                exhibitorBooth['userName'] = _userLogin
                exhibitorBooth['exhibitor'] = _exhibitor
                exhibitorBooth['name'] = exhibitor['name']
                exhibitorBooth['email'] = exhibitor['email']
                exhibitorBooth['contactNo'] = exhibitor['contactNo']
                exhibitorBooth['boothNo'] = boothNo
                _exhibitorBooth = ExhibitorBooth(**exhibitorBooth)
                _exhibitorBooth.save()
        qualifiers = model_fields['Qualifier']
        qualifierModels = dict()
        for qualifier in qualifiers:
            qualifierType = qualifier['qualifierType']
            del qualifier['qualifierType']
            # Save qualifierType , create if not exists
            _qualifierType = _getObjectORNone(QualifierType, qualifierType=qualifierType)
            if not _qualifierType:
                _qualifierType = QualifierType(qualifierType=qualifierType)
                _qualifierType.save()
            qualifierName = qualifier['qualifierName']
            qualifier['qualifierTypeID'] = _qualifierType
            for exhibitorName in exhibitorModels:
                qualifierModels[exhibitorName] = dict()
                exhibitor = exhibitorModels[exhibitorName]                
                # Save qualifier , create if not exists
                _qualifier = _getObjectORNone(Qualifier, exhibitor=exhibitor, qualifierName=qualifierName)
                if not _qualifier:
                    qualifier['exhibitor'] = exhibitor
                    _qualifier = Qualifier(**qualifier)
                    _qualifier.save()
                qualifierModels[exhibitorName][qualifierName] = _qualifier
        questions = model_fields['Questions']
        for question in questions:
            qualifierName = question['qualifierName']
            questionSeq = question['questionSeq']
            del question['qualifierName']
            del question['questionSeq']    
            # Save question
            _question = Question(**question)
            _question.save()
            for exhibitorName in exhibitorModels:
                # Save qualifier question
                qualifierQuestions = dict()
                qualifierQuestions['question'] = _question
                qualifierQuestions['qualifier'] = qualifierModels[exhibitorName][qualifierName]
                qualifierQuestions['seq'] = questionSeq
                _qualifierQuestions = QualifierQuestions(**qualifierQuestions)
                _qualifierQuestions.save()
        settings = model_fields['Settings']
        for setting in settings:
            settingType = setting['settingType']
            settingName = setting['settingName']
            # Save setting , create if not exists
            _setting = _getObjectORNone(Settings, settingType=settingType, settingName=settingName)
            if not _setting:
                _setting = Settings(settingType=settingType, settingName=settingName)
                _setting.save()
            tradeshowSettings = dict()
            tradeshowSettings['tradeshow'] = _tradeshow
            tradeshowSettings['setting'] = _setting
            tradeshowSettings['settingValue'] = setting['settingValue']
            if setting.get('defaultSettingValue'):
                tradeshowSettings['defaultSettingValue'] = setting['defaultSettingValue']
            _tradeshowSetting = TradeshowSettings(**tradeshowSettings)
            _tradeshowSetting.save()
        #raise Exception("Unable to save tradeshow")

def _build_json(file_path):
    """
    """
    current_model_name = ''
    current_column_names = []
    models_json = dict() 
    status_code = 0
    message = ''
    try:
        # Parse the xlsx file and get the rows
        from pyexcel_xlsx import get_data
        data = get_data(file_path)
        sheet_name = data.keys()[0]
        rows = data[sheet_name]
        for row in rows:
            # Row is empty
            if not row:
                continue
            log.info("Processing row: [%s]" % row)
            model_name = _get_model_name(row[0])
            # Check if the model name is valid
            if model_name:
                 if model_name not in model_names:
                    log.info("ImportTradeshow: _get_model_name, Invalid model name, [%s]" % model_name)
                    raise Exception("ImportTradeshow: _get_model_name, Invalid model name, [%s]" % model_name)
                 else:
                    # Get the columns for Model
                    columns = row[1:]
                    columns = [column.strip() for column in columns]
                    # Validate the columns
                    result = _validate_model_columns(model_name, columns)
                    status, message = result
                    if not status:
                        raise Exception(message)
                    # Set the  current model    
                    current_model_name = model_name
                    current_column_names = columns
                    if not models_json.has_key(model_name):
                        models_json[model_name] = []
                    continue
            if not current_model_name:
                continue
            column_values = row[1:]
            model_record = dict(zip(current_column_names, column_values))
            models_json[current_model_name].append(model_record)
    except Exception as ex:
        status_code = -1
        message = 'Unable to build the json.'
        log.info("ImportTradeshow:_build_json, Exception: [%s]" % str(ex))
        log.info(traceback.print_exc())
    return (status_code, message, models_json)


def _get_model_name(row_data):
    """
    """
    _model_name = row_data
    # First column has None value
    if _model_name is None:
        return ''
    _model_name = _model_name.strip() 
    # First column has empty space
    if not _model_name:
        return ''
    return _model_name

def _validate_model_columns(model_name, columns):
    """
    """
    log.info("Import Tradeshow: ModelName: [%s], Columns: [%s]" % (model_name, columns))
    valid_columns = modelColumns.get(model_name, [])
    if columns != valid_columns:
        log.info("ImportTradeshow: _validate_model_columns, Model columns mismatch, modelName: [%s],  validColumns: [%s]" % (model_name, valid_columns))
        return (False, 'Model columns mismatch.')
    return (True, '')

def _validateFields(fields, fieldsKey, isModel=False):
    """Validate the fields.
    """
    log.info("ImportTradeshow: _validateFields, fields: [%s], fieldsKey: [%s], isModel: [%s]" % (fields, fieldsKey, isModel))
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
                        if isinstance(fieldValue, datetime):
                            validatedFields[field] = fieldValue
                        else:
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
        log.info("ImportTradeshow:_validateFields, ValueError Exception: [%s]" % str(ex))
    except Exception as ex:
        log.info("ImportTradeshow:_validateFields, Exception: [%s]" % str(ex))
        statusCode = errorCodes.VALIDATE_MODEL_FIELD_EXCEPTION            
        message = "Got Exception in _validateFields, Exception: [%s]" % str(ex)        
    # Validation failed         
    return (statusCode, message, {})

def _validateModels(model_fields):
    """Validate the models and there dependant models.
       Validations :
                    Check that data is available for all the models
                    No of addresses should match the no of exhibitors + 1 (Tradeshow address)
                    Verify the mapping of addresses to exhibitor and tradeshow.            
                    Tradeshow StartDate endDate validation
                    Verify that end date should always be greated than start date
                    Verify fields count matches total fields        
                    Verify field sequence values
                    Verify for duplicate field names
                    Verify if any duplicate display names
                    Verify badgeIDFieldSeq
                    Verify badgeDataFieldSeq
                    Verify that valid question widget is provided
                    verify that questions exists for every qualifier
                    Verify that qualifier does not have duplicate question sequences    
    """
    log.info("ImportTradeshow: _validateModels, model_fields: [%s]" % model_fields)
    statusCode = 0
    message = ''
    try:
        timeFormat = settings.TRADESHOW_TIME_FORMAT
        # Check that data is available for all the models
        for model_name in model_names:
            print model_name
            _model = model_fields.get(model_name, [])
            if not _model:
                statusCode = -1                
                message = "No data available for %s" % model_name
                raise ValueError(message)
        # No of addresses should match the no of exhibitors + 1 (Tradeshow address)
        addressList =  model_fields['Address']
        addressCount = len(addressList)
        exhibitorList =  model_fields['Exhibitor']
        exhibitorCount = len(exhibitorList)
        if addressCount != (exhibitorCount+1):
            statusCode = -1
            log.info("Invalid no of addresses provided, Address Count: [%s], Exhibitors Count: [%s]" % (addressCount, exhibitorCount))
            message = "Invalid no of addresses provided."
            raise ValueError(message)
        # Verify the mapping of addresses to exhibitor and tradeshow.            
        addressNames = [address['name'] for address in addressList]
        exhibitorNames = [exhibitor['name'] for exhibitor in exhibitorList]
        tradeshow = model_fields['Tradeshow'][0]
        tradeshowName = tradeshow['name']
        # Verify tradeshow address mapping
        if tradeshowName != addressNames[0]: # First address will always be address of tradeshow
            statusCode = -1
            log.info("Invalid Address mapping for tradeshow, Tradeshow Name: [%s], Address Name: [%s]" % (tradeshowName, addressNames[0]))
            message = "Invalid Address mapping for tradeshow."
            raise ValueError(message)
        # Verify exhibitor address mapping
        _addressNames = addressNames[1:]
        if exhibitorNames != _addressNames: # Address order and exhibitor order should be same
            statusCode = -1
            log.info("Invalid address mapping for exhibitors, Exhibitor Namse: [%s], Address Names: [%s]" % (exhibitorNames, _addressNames))
            message = "Invalid address mapping for exhibitors."
            raise ValueError(message)
        # Verify that end date should always be greated than start date
        startDate = tradeshow['startDate']
        endDate = tradeshow['endDate']
        if not (endDate > startDate):
            statusCode = -1
            log.info("Invalid start/end dates for tradeshow, Start Date: [%s], End Date: [%s]" % (startDate, endDate))
            message = "Invalid start/end dates for tradeshow."
            raise ValueError(message)
        # Verify fields count matches total fields        
        mappping = model_fields['Mapping'][0]
        fieldsList = model_fields['Fields']
        fieldsCount = len(fieldsList)        
        if fieldsCount != mappping['totalFields']:
            statusCode = -1
            log.info("Fields count not matching with totalFields, Fields Count: [%s], Total Fields: [%s]" % (fieldsCount, mappping['totalFields']))
            message = "Fields count not matching with totalFields."
            raise ValueError(message)
        fieldNames = []
        displayNames = []
        fieldSequences = []
        badgeIDFieldSeq = badgeDataFieldSeq = None
        for field in fieldsList:
            fieldNames.append(field['name'])
            displayNames.append(field['displayName'])
            fieldSequences.append(field['fieldSeq'])
            if field['name'] == "badgeID":
                badgeIDFieldSeq = field['fieldSeq']
            elif field['name'] == "badgeData":
                badgeDataFieldSeq = field['fieldSeq']        
        # Verify field sequence values
        _fieldSequences = list(set(fieldSequences)) # Filter out any duplicate sequences
        if len(_fieldSequences) != fieldsCount:
            statusCode = -1
            log.info("Duplicate field sequence provided, Fields Count: [%s], Field Sequences: [%s]" % (fieldsCount, fieldSequences))
            message = "Duplicate field sequence provided."
            raise ValueError(message)
        # Verify for duplicate names
        _fieldNames = list(set(fieldNames)) 
        if len(fieldNames) != len(_fieldNames):
            statusCode = -1
            log.info("Duplicate field name provided, Fields Names: [%s]" % (fieldNames))
            message = "Duplicate field name provided."
            raise ValueError(message)
        # Verify if any duplicate display names
        _displayNames = list(set(displayNames)) 
        if len(displayNames) != len(_displayNames):
            statusCode = -1
            log.info("Duplicate display name provided, Display Names: [%s]" % (displayNames))
            message = "Duplicate display name provided."
            raise ValueError(message)            
        # Verify badgeIDFieldSeq
        if mappping['badgeIDFieldSeq'] != badgeIDFieldSeq:
            statusCode = -1
            log.info("Invalid badgeIDFieldSeq, Mapping badgeIDFieldSeq: [%s], Fields badgeIDFieldSeq: [%s]" % (mappping['badgeIDFieldSeq'], badgeIDFieldSeq))
            message = "Invalid badgeIDFieldSeq."
            raise ValueError(message)            
        # Verify badgeDataFieldSeq
        if mappping['badgeDataFieldSeq'] != badgeDataFieldSeq:
            statusCode = -1
            log.info("Invalid badgeDataFieldSeq, Mapping badgeDataFieldSeq: [%s], Fields badgeDataFieldSeq: [%s]" % (mappping['badgeDataFieldSeq'], badgeDataFieldSeq))
            message = "Invalid badgeDataFieldSeq."
            raise ValueError(message)
        # Build qualifier question counts mapping
        qualifierList = model_fields['Qualifier']
        qualifiers = dict()
        for qualifier in qualifierList:
            _name = qualifier['qualifierName']
            qualifiers[_name] = qualifier['totalQuestions']
        qualifierQuestions = dict()
        questionList = model_fields['Questions']
        for question in questionList:
            # Verify that valid question widget is provided
            _widget = question['widgetName'] 
            if _widget not in widgets:
                statusCode = -1
                log.info("Invalid Question widget provided, Question: [%s], Question Widget: [%s]" % (question['question'], _widget))
                message = "Invalid Question widget provided."
                raise ValueError(message)
            _name = question['qualifierName']
            qualifierQuestions.setdefault(_name, []).append(question['questionSeq'])
        # Verify that questions exists for every qualifier
        qualifierNames = qualifiers.keys()
        questionQualifierNames = qualifierQuestions.keys()
        qualifierNames.sort()
        questionQualifierNames.sort()
        if qualifierNames != questionQualifierNames:
            statusCode = -1
            log.info("Invalid mapping for Questions and Qualifiers, Qualifier Names: [%s], Question Qualifier Names: [%s]" % (qualifierNames, questionQualifierNames))
            message = "Invalid mapping for Questions and Qualifiers"
            raise ValueError(message) 
        for qualifierName in qualifierQuestions:
            questionSequences = qualifierQuestions[qualifierName]
            _questionSequences = list(set(questionSequences))
            # Verify that qualifier does not have duplicate question sequences
            if len(questionSequences) != len(_questionSequences):
                statusCode = -1
                log.info("Invalid Question sequence provided, Qualifier Name: [%s], Question Sequences: [%s]" % (qualifierName, questionSequences))
                message = "Invalid Question sequence provided."
                raise ValueError(message)
            totalQuestions = qualifiers[qualifierName]
            if totalQuestions != len(questionSequences):
                statusCode = -1
                log.info("Total questions count and questions not matching, Total Questions: [%s], Question Sequences: [%s]" % (totalQuestions, questionSequences))
                message = "Total questions count and questions not matching."
                raise ValueError(message)
        # Validation successful                  
        return (statusCode, message)
    except ValueError as ex:
        log.info("ImportTradeshow:_validateModels, ValueError Exception: [%s]" % str(ex))
    except Exception as ex:
        log.info("ImportTradeshow:_validateModels, Exception: [%s]" % str(ex))
        statusCode = errorCodes.VALIDATE_MODEL_FIELD_EXCEPTION            
        message = "Got Exception in _validateModels, Exception: [%s]" % str(ex)  
        raise ex
        #raise ex
    # Validation failed         
    return (statusCode, message)


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

main()
#if __name__ == "__main__":
#    main()
