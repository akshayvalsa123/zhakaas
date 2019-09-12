# This mapping is for model fields
modelFieldMappings = dict()
# This mapping is for validating fields
validationFieldMappings = dict()

leadsData = dict()
leadsData['leads'] = {'type': 'object', 'required': True}
leadsData['deviceDetails'] = {'type': 'object', 'required': False}
leadsData['tradeshowID'] = {'type': 'integer', 'required': True}
leadsData['exhibitorID'] = {'type': 'integer', 'required': True}
leadsData['userName'] = {'type': 'text', 'required': True}
validationFieldMappings['LeadsData'] = leadsData


# TODO: Build this mapping from models
deviceDetails = dict()
deviceDetails['deviceID'] = {'type': 'text', 'required': True}
deviceDetails['deviceName'] = {'type': 'text', 'required': True}
deviceDetails['deviceModel'] = {'type': 'text', 'required': True}
deviceDetails['appVersion'] = {'type': 'text', 'required': True}
deviceDetails['isActive'] = {'type': 'boolean', 'required': True}
deviceDetails['initTime'] = {'type': 'datetime', 'required': True}
deviceDetails['syncTime'] = {'type': 'datetime', 'required': True}
modelFieldMappings['DeviceDetails'] = deviceDetails

leadDetails = dict()
leadDetails['device'] = {'type': 'modelObject', 'required': False}
leadDetails['scanType'] = {'type': 'text', 'required': True}
leadDetails['syncID'] = {'type': 'text', 'required': True}
leadDetails['captureTime'] = {'type': 'datetime', 'required': True}
leadDetails['leadSyncStatus'] = {'type': 'text', 'required': True}
leadDetails['leadType'] = {'type': 'text', 'required': True}
leadDetails['rating'] = {'type': 'text', 'required': False}
leadDetails['comment'] = {'type': 'text', 'required': False}
modelFieldMappings['LeadDetails'] = leadDetails

# Model mappings for all the models required to create tardeshow.
addressFields = dict()
addressFields['address1'] = {'type': 'text', 'required': True}
addressFields['address2'] = {'type': 'text', 'required': False}
addressFields['street'] = {'type': 'text', 'required': False}
addressFields['city'] = {'type': 'text', 'required': True}
addressFields['country'] = {'type': 'text', 'required': True}
addressFields['zipcode'] = {'type': 'text', 'required': True}
addressFields['name'] = {'type': 'text', 'required': True} # name of the tradeshow/exhibitor
modelFieldMappings['Address'] = addressFields

tradeshowFields = dict()
tradeshowFields['name'] = {'type': 'text', 'required': True}
tradeshowFields['nameCode'] = {'type': 'text', 'required': False}
tradeshowFields['startDate'] = {'type': 'datetime', 'required': True}
tradeshowFields['endDate'] = {'type': 'datetime', 'required': True}
tradeshowFields['email'] = {'type': 'text', 'required': False}
tradeshowFields['contactNo'] = {'type': 'text', 'required': True}
tradeshowFields['adminPassword'] = {'type': 'text', 'required': True}
tradeshowFields['supportMessage'] = {'type': 'text', 'required': False}
tradeshowFields['website'] = {'type': 'text', 'required': False}
tradeshowFields['timeZone'] = {'type': 'text', 'required': False}
modelFieldMappings['Tradeshow'] = tradeshowFields

mappingFields = dict()
mappingFields['totalFields'] = {'type': 'integer', 'required': True}
mappingFields['badgeIDFieldSeq'] = {'type': 'integer', 'required': True}
mappingFields['badgeDataFieldSeq'] = {'type': 'integer', 'required': True}
modelFieldMappings['Mapping'] = mappingFields

fieldFields = dict()
fieldFields['name'] = {'type': 'text', 'required': True}
fieldFields['displayName'] = {'type': 'text', 'required': True}
fieldFields['fieldSeq'] = {'type': 'text', 'required': True}
fieldFields['description'] = {'type': 'text', 'required': False}
modelFieldMappings['Fields'] = fieldFields

exhibitorFields = dict()
exhibitorFields['name'] = {'type': 'text', 'required': True}
exhibitorFields['email'] = {'type': 'text', 'required': True}
exhibitorFields['contactNo'] = {'type': 'text', 'required': True}
exhibitorFields['alternateEmail'] = {'type': 'text', 'required': False}
exhibitorFields['alternateContactNo'] = {'type': 'text', 'required': False}
exhibitorFields['licenseCount'] = {'type': 'integer', 'required': True}
exhibitorFields['userName'] = {'type': 'text', 'required': True}
exhibitorFields['password'] = {'type': 'text', 'required': True}
modelFieldMappings['Exhibitor'] = exhibitorFields

userLoginFields = dict()
userLoginFields['userName'] = {'type': 'text', 'required': True}
userLoginFields['password'] = {'type': 'text', 'required': True}
userLoginFields['isActive'] = {'type': 'boolean', 'required': True}
modelFieldMappings['UserLogin'] = userLoginFields

exhibitorBoothFields = dict()
exhibitorBoothFields['name'] = {'type': 'text', 'required': True}
exhibitorBoothFields['email'] = {'type': 'text', 'required': True}
exhibitorBoothFields['contactNo'] = {'type': 'text', 'required': True}
exhibitorBoothFields['boothNo'] = {'type': 'text', 'required': False}
modelFieldMappings['ExhibitorBooth'] = exhibitorBoothFields

qualifierTypeFields = dict()
qualifierTypeFields['qualifierType'] = {'type': 'text', 'required': True}
modelFieldMappings['QualifierType'] = qualifierTypeFields

qualifierFields = dict()
qualifierFields['qualifierName'] = {'type': 'text', 'required': True}
qualifierFields['screenNo'] = {'type': 'integer', 'required': True}
qualifierFields['ansFormat'] = {'type': 'integer', 'required': True}
qualifierFields['totalQuestions'] = {'type': 'integer', 'required': True}
modelFieldMappings['Qualifier'] = qualifierFields

questionFields = dict()
questionFields['question'] = {'type': 'text', 'required': True}
questionFields['widgetName'] = {'type': 'text', 'required': True}
questionFields['options'] = {'type': 'text', 'required': True}
modelFieldMappings['Questions'] = questionFields

settingsFields = dict()
settingsFields['settingType'] = {'type': 'text', 'required': True}
settingsFields['settingName'] = {'type': 'text', 'required': True}
modelFieldMappings['Settings'] = settingsFields

tradeshowSettingsFields = dict()
tradeshowSettingsFields['settingValue'] = {'type': 'text', 'required': True}
tradeshowSettingsFields['defaultSettingValue'] = {'type': 'text', 'required': False}
tradeshowSettingsFields['options'] = {'type': 'text', 'required': False}
modelFieldMappings['TradeshowSettings'] = tradeshowSettingsFields
