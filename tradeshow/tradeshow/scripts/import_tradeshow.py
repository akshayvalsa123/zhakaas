import os
import json
import logging 
import traceback
from datetime import datetime
from django.conf import settings
from django.db import transaction


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

from tradeshow.common.exceptions import ImportException
from tradeshow.common.utils import _buildResponse
from tradeshow.common.field_mappings import modelFieldMappings, validationFieldMappings
from tradeshow.common import error_codes as errorCodes


# Initialise Logger
# TODO: logging not propogating need to work on it.
log = logging.getLogger(__name__)
if True:
    #hdlr = logging.StreamHandler()
    hdlr = logging.FileHandler('/opt/projects/lead_management/logs/import_ts.log')
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
modelColumns['Settings'] = ['settingType', 'settingName', 'settingValue', 'defaultSettingValue', 'options']


class ImportTradeshow(object):
    """Class to handle import tradeshow.
    """

    def __init__(self):
        """Init function.
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
        self.modelColumns['Settings'] = ['settingType', 'settingName', 'settingValue', 'defaultSettingValue', 'options']
        self.widgets = set(['EditText', 'Checkbox', 'Spinner'])
        self.response = dict()
        self.response['response'] = {}
        self.response['responseHeader'] = {'status': 0}
        log.info("ImportTradeshow:__init__")

    def importFromFile(self, tradeshowFile):
        """Import the tradeshow from XLSX file
        """
        try:
            # Check if the tradeshow file exists.
            if not os.path.exists(tradeshowFile):
                statusCode = errorCodes.FILE_DOES_NOT_EXISTS
                message = "Import failed, File does not exists."
                log.info("ImportTradeshow:importFromFile, Tradeshow import failed, File [%s] does not exists.." % tradeshowFile)
                return (statusCode, message)

            # Build the josn from tradeshow file
            statusCode, message, tradeshowJson = self._getTradeshowJson(tradeshowFile)            
            log.info("ImportTradeshow:importFromFile, _getTradeshowJson: statusCode: [%s], message: [%s], tradeshowJson:[%s]" %(statusCode, message, tradeshowJson))            
            if statusCode != 0:            
                log.info("ImportTradeshow:importFromFile, Unable to build tradeshow json.")
                message = "Import failed, Unable to build tradeshow json."
                return (statusCode, message)

            # Verify if any models information is missing.
            _modelNames = set(tradeshowJson.keys())
            missingModels = self.modelNames - _modelNames
            if missingModels:
                log.info("ImportTradeshow:importFromFile, Not all models information provided.Missing models: [%s]" % missingModels)            
                statusCode = errorCodes.IMPORT_MODEL_MISSING
                message = "Import failed, Missing models information."            
                return (statusCode, message)

            # Validate each indivisual models information
            _models = dict()
            for modelName in tradeshowJson:
                log.info("ImportTradeshow:importFromFile, processing model: [%s]" % modelName)
                # Fetch the model information
                modelRecords = tradeshowJson[modelName]
                for modelRecord in modelRecords:
                    log.info("ImportTradeshow:importFromFile, processing modelRecord: [%s]" % modelRecord)
                    result = _validateFields(modelRecord, modelName, isModel=True)
                    statusCode, message, validatedFields = result
                    log.info("ImportTradeshow:importFromFile, _validateFields: statusCode: [%s], message: [%s], validatedFields: [%s]" % (statusCode, message, validatedFields))            
                    if statusCode != 0:
                        log.info("ImportTradeshow:importFromFile, model validation failed.")
                        return (statusCode, message)
                    # Prepare models information
                    _models.setdefault(modelName, []).append(validatedFields)

            # Check if file has records
            if not _models:
                log.info("ImportTradeshow:importFromFile, No records available.")            
                statusCode = errorCodes.FILE_DOES_NOT_HAVE_RECORDS
                message = "Import failed, No records available."
                return (statusCode, message)
            log.info("=========== ImportTradeshow:importFromFile, Indivisual Models validation successful. ===========")
            # Delete the existing tradeshow if any exists.
            result = self._deleteExistingTradeshow(_models)
            statusCode , message = result
            log.info("ImportTradeshow:importFromFile, _deleteExistingTradeshow: statusCode: [%s], message: [%s]" %(statusCode, message))
            if statusCode != 0:            
                log.info("ImportTradeshow:importFromFile, Error in deleting existing tradeshow.")
                return (statusCode, message)

            # Validate the models and there dependant models.
            result = _validateModels(_models)
            statusCode, message = result
            log.info("ImportTradeshow:importFromFile, _validateModels: statusCode: [%s], message: [%s]" %(statusCode, message))
            if statusCode != 0:
                log.info("ImportTradeshow:importFromFile, Error in validating tradeshow models.")
                return (statusCode, message)

            # Save the tradeshow
            saveInfo = dict()
            try:            
                self._saveTardeshow(_models)
                statusCode = 0
                message = ""
            except Exception as ex:
                statusCode = errorCodes.SAVE_TRADESHOW_EXCEPTION
                message = "Error in save Tradeshow, Exception: %s" % str(ex)
                log.info("ImportTradeshow:importFromFile, _saveTardeshow: statusCode: [%s], message: [%s]" %(statusCode, message))
                return (statusCode, "Error in save Tradeshow.")

            if False: # TODO: As of now we are not using login info will need the same later.
                tradeshowName = _models['Tradeshow'][0]['name']
                result = self._getTradeshowLogins(tradeshowName)
                statusCode, message, loginInfo = result
                log.info("ImportTradeshow:importFromFile, _getTradeshowLogins: statusCode: [%s], message: [%s], loginInfo: [%s]" %(statusCode, message, loginInfo))
                if statusCode != 0:
                    log.info("ImportTradeshow:importFromFile, Error in fetching tradeshow logins.")
                    return (statusCode, message)
        
            log.info("######## ImportTradeshow:importFromFile, Save tradeshow successful. ########")
            message = "Save tradeshow successful."
            return (statusCode, message)
        except ImportException as ex:
            raise ex
            #response = _buildResponse(ex.statusCode, ex.message)
            log.info("ImportTradeshowView:post, ImportException  statusCode: [%s], message: [%s]" % (ex.statusCode, ex.message))
            return (ex.statusCode, ex.message)
        except Exception as ex:
            raise ex
            log.info("ImportTradeshow:importFromFile, Exception: Error:[%s]" % str(ex))
            statusCode = errorCodes.IMPORT_FROM_FILE_EXCEPTION
            message = "Exception in tradeshow import."
            return (statusCode, message)

    def _getTradeshowJson(self, tradeshowFile):
        """
        """
        currentModelName = ''
        currentColumnNames = []
        modelJson = dict() 
        statusCode = 0
        message = ''
        def _cleanModelName(data):
            """Clean the model name.
            """
            _modelName = data
            # First column has None value
            if _modelName is None:
                return ''
            _modelName = _modelName.strip() 
            # First column has empty space
            if not _modelName:
                return ''
            return _modelName

        try:
            # Parse the xlsx file and get the rows
            from pyexcel_xlsx import get_data
            tradeshowData = get_data(tradeshowFile)
            sheetName = tradeshowData.keys()[0]
            _tradeshowRows = tradeshowData[sheetName]
            tradeshowRows = []
            for _tradeshowRow in _tradeshowRows:
                log.info(_tradeshowRow)
                _row = []
                for item in _tradeshowRow:
                    if isinstance(item, basestring):
                        _row.append(item.strip())
                    else:
                        _row.append(item)
                tradeshowRows.append(_row)

            for tradeshowRow in tradeshowRows:
                # Row is empty
                if not tradeshowRow:
                    continue
                log.info("ImportTradeshow:_getTradeshowJson, Processing tradeshowRow: [%s]" % tradeshowRow)
                modelName = _cleanModelName(tradeshowRow[0])
                # Model name is available in first column so set the current model and its columns.
                if modelName:
                    log.info("ImportTradeshow:_getTradeshowJson, Processing Model: [%s]" % modelName)
                    # Check if the model name is valid
                    if modelName not in self.modelNames:
                        statusCode = errorCodes.INVALID_MODEL_NAME
                        message = "Invalid model name, modelName: [%s]" % modelName
                        raise ImportException(statusCode, message)
                    # Get the columns for Model
                    columns = tradeshowRow[1:]
                    columns = [column.strip() for column in columns]
                    # Validate the columns
                    result = self._validateModelColumns(modelName, columns)
                    statusCode, message = result
                    if statusCode != 0:
                        raise ImportException(statusCode, message)
                    log.info("ImportTradeshow:_getTradeshowJson, Model columns validated successfully.")
                    # Set the current model  name and column names
                    currentModelName = modelName
                    currentColumnNames = columns
                    # Set the models mapping
                    if not modelJson.has_key(modelName):
                        modelJson[modelName] = []
                    continue
                # No model has been found yet
                if not currentModelName:
                    continue
                # Save the record for respective model.
                columnValues = tradeshowRow[1:]
                modelRecord = dict(zip(currentColumnNames, columnValues))
                modelJson[currentModelName].append(modelRecord)
        except ImportException as ex:
            log.info("ImportTradeshow:_getTradeshowJson ImportException, Exception: [%s]" % ex.message)
        except Exception as ex:
            log.info("ImportTradeshow:_getTradeshowJson Error, Exception: [%s]" % str(ex))
            status_code = errorCodes.GET_TRADESHOW_JSON_EXCEPTION
            message = "Unable to get tradeshow json."            
        return (statusCode, message, modelJson)

    def _validateModelColumns(self, modelName, columns):
        """
        """
        log.info("ImportTradeshow:_validateModelColumns ModelName: [%s], Columns: [%s]" % (modelName, columns))
        validColumns = self.modelColumns.get(modelName, [])
        if columns != validColumns:
            log.info("ImportTradeshow:_validateModelColumns Model columns mismatch, modelName: [%s], validColumns: [%s]" % (modelName, validColumns))
            return (errorCodes.INVALID_MODEL_COLUMNS, 'Model columns mismatch.')
        return (0, '')

    def _deleteExistingTradeshow(self, models):
        """
        """
        statusCode = 0
        message = ""
        tradeshow = models['Tradeshow'][0]
        # Get the tradehsow address
        tradeshowName = tradeshow['oldName']
        with transaction.atomic():
            tradeshowObj = _getObjectORNone(Tradeshow, name=tradeshowName)
            # If tradeshow does not exists return
            if not tradeshowObj:
                log.info("ImportTradeshow:_deleteExistingTradeshow, Tradeshow does not exists, Name: [%s]" % tradeshowName)
                return (statusCode, "Tradeshow does not exists, Name: [%s]" % tradeshowName)
            # If tradeshow exists so delete the same
            log.info("ImportTradeshow:_deleteExistingTradeshow, Tradeshow exists, Name/ID: [%s/%s]" % (tradeshowObj.name, tradeshowObj.id))
            leadCount = LeadMaster.objects.filter(tradeshow=tradeshowObj).count()
            if leadCount:
                log.info("ImportTradeshow:_deleteExistingTradeshow, Tradeshow has leads, cannot update/delete tradeshow.")
                return (errorCodes.TRADESHOW_HAS_LEADS, "Tradeshow has leads, cannot update/delete tradeshow.")                
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
            log.info("ImportTradeshow:_deleteExistingTradeshow, Deleting tradeshowAddress: [%s]" % tradeshowAddress)
            tradeshowAddress.delete()
            # Delete exhibitor addresses    
            log.info("ImportTradeshow:_deleteExistingTradeshow, Deleting exhibitorAddresses: [%s]" % exhibitorAddresses)
            for exhibitorAddress in exhibitorAddresses:
                exhibitorAddress.delete()
            # Delete userLogins
            log.info("ImportTradeshow:_deleteExistingTradeshow, Deleting userLogins: [%s]" % userLogins)
            for userLogin in userLogins:
                userLogin.delete()
            # Delete questions
            log.info("ImportTradeshow:_deleteExistingTradeshow, Deleting questions: [%s]" % questions)
            for question in questions:
                question.delete()
            # Delete Tradeshow, this will do a cascade delete and hence will also delete below records
            # Mappings, Exhibitors, Exhibitor booths, Fields mappings, Qualifiers, Qualifier questionss
            tradeshowObj.delete()
        return (statusCode, message)

    def _saveTardeshow(self, models):
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
		# Create default exhibitor address
		tradeshow = models['Tradeshow'][0]
		exhb_default_address_name = '%s-default-address' % tradeshow['name']
		exhb_default_address = Address.objects.filter(address1=exhb_default_address_name).first()
		if not exhb_default_address:
			exhb_default_address = Address.objects.create(address1=exhb_default_address_name)
			exhb_default_address.save()

        with transaction.atomic():
            addressModels = {}
            # Save address object for tradeshow and exhibitors
            addressList = models['Address']
            for address in addressList:
                # Get the name for which address is to be built
                name = address['name']
                del address['name']
                # Save the address
                _address = Address(**address)
                _address.save()
                addressModels[name] = _address
            log.info("ImportTradeshow:_saveTardeshow, All addresses saved.")
            # Save tradeshow
            tradeshow = models['Tradeshow'][0]
            # Get the tradehsow address
            tradeshowName = tradeshow['name']    
            tradeshowObj = _getObjectORNone(Tradeshow, name=tradeshowName)
            # Create new tradeshow
            if tradeshowObj:
                raise Exception("Tradeshow already exists.")
            tradeshow['address'] = addressModels[tradeshowName]
            # Delete the old name
            if tradeshow.has_key('oldName'):
                oldName = tradeshow['oldName']
                del tradeshow['oldName']
            _tradeshow = Tradeshow(**tradeshow)
            _tradeshow.save()
            log.info("ImportTradeshow:_saveTardeshow, Tradeshow saved.")
            # Save Mapping
            mapping = models['Mapping'][0]
            mapping['tradeshow'] = _tradeshow
            _mapping = Mapping(**mapping)
            _mapping.save()
            log.info("ImportTradeshow:_saveTardeshow, Mapping saved.")
            # Save field and fieldsMapping
            fields = models['Fields']
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
            log.info("ImportTradeshow:_saveTardeshow, Field Mappings saved.")
            # Save Exhibitor
            exhibitors = models['Exhibitor']
            exhibitorModels = dict()
            for exhibitor in exhibitors:
                name = exhibitor['name']
                userName = exhibitor['userName']
                password = exhibitor['password']
                licenseCount = exhibitor['licenseCount']
                del exhibitor['userName']
                del exhibitor['password']
                exhibitor['tradeshow'] = _tradeshow
				if addressModels.get(name):
                	exhibitor['address'] = addressModels[name]
				else:
					exhibitor['address'] = exhb_default_address
				log.info('exhibitor: [%s]' % exhibitor)
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
            log.info("ImportTradeshow:_saveTardeshow, exhibitor, exhibitorBooth and userLogins saved.")
            qualifiers = models['Qualifier']
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
                    if not qualifierModels.has_key(exhibitorName):
                        qualifierModels[exhibitorName] = dict()
                    exhibitor = exhibitorModels[exhibitorName]                
                    # Save qualifier , create if not exists
                    _qualifier = _getObjectORNone(Qualifier, exhibitor=exhibitor, qualifierName=qualifierName)
                    if not _qualifier:
                        qualifier['exhibitor'] = exhibitor
                        _qualifier = Qualifier(**qualifier)
                        _qualifier.save()
                    qualifierModels[exhibitorName][qualifierName] = _qualifier
            log.info("ImportTradeshow:_saveTardeshow, qualifierType and qualifier saved.")
            questions = models['Questions']
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
            log.info("ImportTradeshow:_saveTardeshow, question and qualifierQuestion saved.")
            settings = models['Settings']
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
            log.info("ImportTradeshow:_saveTardeshow, setting and tradesetting saved.")
            #raise Exception("Unable to save tradeshow")

    def _getTradeshowLogins(self, tradeshowName):
        """
        """
        statusCode = 0
        message = ''
        tradeshowLogins = dict()
        try:
            tradeshow = _getObjectORNone(Tradeshow, name=tradeshowName)
            exhibitors = Exhibitor.objects.filter(tradeshow=tradeshow)
            exhibitorBooths = ExhibitorBooth.objects.filter(exhibitor__in=exhibitors)
            _exhibitorLogins = dict()
            for exhibitorBooth in exhibitorBooths:
                _name = exhibitorBooth.exhibitor.name
                loginInfo = dict()
                loginInfo['userName'] = exhibitorBooth.userName.userName
                loginInfo['password'] = exhibitorBooth.userName.password
                _exhibitorLogins.setdefault(_name, []).append(loginInfo)
            exhibitorLogins = list()
            for exhibitorName in _exhibitorLogins:
                loginInfo = dict()
                loginInfo['name'] = exhibitorName
                loginInfo['logins'] = _exhibitorLogins[exhibitorName]
                exhibitorLogins.append(loginInfo)
            tradeshowLogins['tradeshowName'] = tradeshowName
            tradeshowLogins['exhibitorLogins'] = exhibitorLogins
        except Exception as ex:
            log.info("ImportTradeshow:_getTradeshowLogins Error, Exception: [%s]" % str(ex))
            statusCode = errorCodes.GET_TRADESHOW_LOGINS_EXCEPTION
            message = "Unable to get tradeshow json."            

        return (statusCode, message, tradeshowLogins)


def _validateFields(fields, fieldsKey, isModel=False):
    """Validate the fields.
    """
    log.info("ImportTradeshow:_validateFields, fields: [%s], fieldsKey: [%s], isModel: [%s]" % (fields, fieldsKey, isModel))
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
                    raise ImportException(statusCode, message)
            # Validation for typed fields like, datetime, integer, boolean
            # TODO: Handle fields which are not mandatory and has type other than text
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
                        raise ImportException(statusCode, message)
                elif fieldInfo['type'] == 'integer':
                    try:
                        parsedFieldValue = int(fieldValue)
                        validatedFields[field] = parsedFieldValue
                    except ValueError as ex:
                        statusCode = errorCodes.INVALID_NUMERIC_VALUE
                        message = "Invalid integer value provided for Field: %s, Value: %s" % (field, fieldValue)
                        raise ImportException(statusCode, message)
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
                        raise ImportException(statusCode, message)
        # Validation successful                        
        return (statusCode, message, validatedFields)
    except ImportException as ex:
        log.info("ImportTradeshow:_validateFields, ImportException Exception: [%s]" % ex.message)
    except Exception as ex:
        log.info("ImportTradeshow:_validateFields, Exception: [%s]" % str(ex))
        statusCode = errorCodes.VALIDATE_MODEL_FIELD_EXCEPTION            
        message = "Got Exception in _validateFields, Exception: [%s]" % str(ex)        
    # Validation failed         
    return (statusCode, message, {})

def _validateModels(models):
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
    log.info("ImportTradeshow: _validateModels, models: [%s]" % models)
    statusCode = 0
    message = ''
    try:
        timeFormat = settings.TRADESHOW_TIME_FORMAT
        # Check that data is available for all the models
        for modelName in modelNames:
            _model = models.get(modelName, [])
            if not _model:
                statusCode = errorCodes.MODEL_INFO_NOT_AVAILABLE
                message = "No data available for %s" % model_name
                raise ImportException(statusCode, message)
        # No of addresses should match the no of exhibitors + 1 (Tradeshow address)
        addressList =  models['Address']
        addressCount = len(addressList)
        exhibitorList =  models['Exhibitor']
        exhibitorCount = len(exhibitorList)
        if False and addressCount != (exhibitorCount+1): # Disable the address count validation , will use the default address
            log.info("Invalid number of addresses provided, Address Count: [%s], Exhibitors Count: [%s]" % (addressCount, exhibitorCount))
            statusCode = errorCodes.EXHIBITOR_ADDRESS_COUNT_MISMATCH
            message = "Invalid number of addresses provided."
            raise ImportException(statusCode, message)
        # Verify the mapping of addresses to exhibitor and tradeshow.            
        addressNames = [address['name'] for address in addressList]
        exhibitorNames = [exhibitor['name'] for exhibitor in exhibitorList]
        tradeshow = models['Tradeshow'][0]
        tradeshowName = tradeshow['name']
        # Verify tradeshow address mapping
        if tradeshowName != addressNames[0]: # First address will always be address of tradeshow
            log.info("Invalid Address mapping for tradeshow, Tradeshow Name: [%s], Address Name: [%s]" % (tradeshowName, addressNames[0]))            
            statusCode = errorCodes.INVALID_TRADESHOW_ADDRESS            
            message = "Invalid Address mapping for tradeshow."
            raise ImportException(statusCode, message)
        # Verify exhibitor address mapping
        _addressNames = addressNames[1:]
        if False and exhibitorNames != _addressNames: # Address order and exhibitor order should be same
            statusCode = errorCodes.EXHIBITOR_ADDRESS_ORDER_MISMATCH
            log.info("Invalid address mapping for exhibitors, Exhibitor Namse: [%s], Address Names: [%s]" % (exhibitorNames, _addressNames))
            message = "Invalid address mapping for exhibitors."
            raise ImportException(statusCode, message)
        # Verify that end date should always be greated than start date
        startDate = tradeshow['startDate']
        endDate = tradeshow['endDate']
        if not (endDate > startDate):
            statusCode = errorCodes.INVALID_START_END_DATE
            log.info("Invalid start/end dates for tradeshow, Start Date: [%s], End Date: [%s]" % (startDate, endDate))
            message = "Invalid start/end dates for tradeshow."
            raise ImportException(statusCode, message)
        # Verify fields count matches total fields        
        mappping = models['Mapping'][0]
        fieldsList = models['Fields']
        fieldsCount = len(fieldsList)        
        if fieldsCount != mappping['totalFields']:
            statusCode = errorCodes.FIELD_COUNT_MISMATCH
            log.info("Fields count not matching with totalFields, Fields Count: [%s], Total Fields: [%s]" % (fieldsCount, mappping['totalFields']))
            message = "Fields count not matching with totalFields."
            raise ImportException(statusCode, message)
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
            statusCode = errorCodes.DUPLICATE_FIELD_SEQUENCE
            log.info("Duplicate field sequence provided, Fields Count: [%s], Field Sequences: [%s]" % (fieldsCount, fieldSequences))
            message = "Duplicate field sequence provided."
            raise ImportException(statusCode, message)
        # Verify for duplicate names
        _fieldNames = list(set(fieldNames)) 
        if len(fieldNames) != len(_fieldNames):
            statusCode = errorCodes.DUPLICATE_FIELD_NAME
            log.info("Duplicate field name provided, Fields Names: [%s]" % (fieldNames))
            message = "Duplicate field name provided."
            raise ImportException(statusCode, message)
        # Verify if any duplicate display names
        _displayNames = list(set(displayNames)) 
        if len(displayNames) != len(_displayNames):
            statusCode = errorCodes.DUPLICATE_FIELD_DISPLAY_NAME
            log.info("Duplicate display name provided, Display Names: [%s]" % (displayNames))
            message = "Duplicate display name provided."
            raise ImportException(statusCode, message)
        # Verify badgeIDFieldSeq
        if mappping['badgeIDFieldSeq'] != badgeIDFieldSeq:
            statusCode = errorCodes.INVALID_BADGEID_FIELD_SEQUENCE
            log.info("Invalid badgeIDFieldSeq, Mapping badgeIDFieldSeq: [%s], Fields badgeIDFieldSeq: [%s]" % (mappping['badgeIDFieldSeq'], badgeIDFieldSeq))
            message = "Invalid badgeIDFieldSeq."
            raise ImportException(statusCode, message)           
        # Verify badgeDataFieldSeq
        if mappping['badgeDataFieldSeq'] != badgeDataFieldSeq:
            statusCode = errorCodes.INVALID_BADGEDATA_FIELD_SEQUENCE
            log.info("Invalid badgeDataFieldSeq, Mapping badgeDataFieldSeq: [%s], Fields badgeDataFieldSeq: [%s]" % (mappping['badgeDataFieldSeq'], badgeDataFieldSeq))
            message = "Invalid badgeDataFieldSeq."
            raise ImportException(statusCode, message)
        # Build qualifier question counts mapping
        qualifierList = models['Qualifier']
        qualifiers = dict()
        for qualifier in qualifierList:
            _name = qualifier['qualifierName']
            qualifiers[_name] = qualifier['totalQuestions']
        qualifierQuestions = dict()
        questionList = models['Questions']
        for question in questionList:
            # Verify that valid question widget is provided
            _widget = question['widgetName'] 
            if _widget not in widgets:
                statusCode = errorCodes.INVALID_QUESTION_WIDGET
                log.info("Invalid Question widget provided, Question: [%s], Question Widget: [%s]" % (question['question'], _widget))
                message = "Invalid Question widget provided."
                raise ImportException(statusCode, message)
            _name = question['qualifierName']
            qualifierQuestions.setdefault(_name, []).append(question['questionSeq'])
        # Verify that questions exists for every qualifier
        qualifierNames = qualifiers.keys()
        questionQualifierNames = qualifierQuestions.keys()
        qualifierNames.sort()
        questionQualifierNames.sort()
        if qualifierNames != questionQualifierNames:
            statusCode = errorCodes.QUESTION_QUALIFIER_MISMATCH
            log.info("Invalid mapping for Questions and Qualifiers, Qualifier Names: [%s], Question Qualifier Names: [%s]" % (qualifierNames, questionQualifierNames))
            message = "Invalid mapping for Questions and Qualifiers"
            raise ImportException(statusCode, message)
        for qualifierName in qualifierQuestions:
            questionSequences = qualifierQuestions[qualifierName]
            _questionSequences = list(set(questionSequences))
            # Verify that qualifier does not have duplicate question sequences
            if len(questionSequences) != len(_questionSequences):
                statusCode = errorCodes.DUPLICATE_QUESTION
                log.info("Invalid Question sequence provided, Qualifier Name: [%s], Question Sequences: [%s]" % (qualifierName, questionSequences))
                message = "Invalid Question sequence provided."
                raise ImportException(statusCode, message)
            totalQuestions = qualifiers[qualifierName]
            if totalQuestions != len(questionSequences):
                statusCode = errorCodes.QUESTION_COUNT_MISMATCH
                log.info("Total questions count and questions not matching, Total Questions: [%s], Question Sequences: [%s]" % (totalQuestions, questionSequences))
                message = "Total questions count and questions not matching."
                raise ImportException(statusCode, message)
        # Validation successful                  
        return (statusCode, message)
    except ImportException as ex:
        log.info("ImportTradeshow:_validateModels, ImportException Exception: [%s]" % ex.message)
    except Exception as ex:
        log.info("ImportTradeshow:_validateModels, Exception: [%s]" % str(ex))
        statusCode = errorCodes.VALIDATE_MODEL_FIELD_EXCEPTION            
        message = "Got Exception in _validateModels, Exception: [%s]" % str(ex)  
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

#obj = ImportTradeshow()

