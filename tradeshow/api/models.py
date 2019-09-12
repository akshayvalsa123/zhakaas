# -*- coding: utf-8 -*-
from django.db import models

class BaseModel(models.Model):
    """BaseModel to hold all the common fields across tables.
    """
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        abstract = True
        
class UserLogin(BaseModel):
    """Table for storing user credentials.
       Desc: Each exhibitor will be given one/more userName-password to login to the application. 
    """
    userName = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    isActive = models.BooleanField()
    
    class Meta:
        db_table = 'UserLogin'

    def __unicode__(self):
        return self.userName

class UserLoginSession(BaseModel):
    """Table for storing user credentials.
       Desc: Each exhibitor will be given one/more userName-password to login to the application. 
    """
    user = models.ForeignKey(UserLogin)
    authToken = models.CharField(max_length=250)
    loginTime = models.DateTimeField(auto_now_add=True)
    logoutTime = models.DateTimeField(null=True, blank=True)
    specialLogin = models.BooleanField(default=False)
    comment = models.CharField(max_length=500, blank=True, null=True)
    device = models.ForeignKey('DeviceDetails', blank=True, null=True)

    class Meta:
        db_table = 'UserLoginSession'

    def __unicode__(self):
        return '%s' %self.id

class Sponsor(BaseModel):
    """Sponsors table.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'Sponsor'
        
    def __unicode__(self):
        return '%s' % self.name

class Industry(BaseModel):
    """Table for storing industry names.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'Industry'
        
    def __unicode__(self):
        return '%s' % self.name

class Address(BaseModel):
    """Address table.
    """
    address1 = models.TextField()
    address2 = models.TextField(blank=True, null=True)
    street = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)        
    country = models.CharField(max_length=50)        
    zipcode = models.CharField(max_length=20)
    
    class Meta:
        db_table = 'Address'    
          
    def __unicode__(self):
        return u'%s, %s %s, %s, %s' % (self.address1, self.city, self.zipcode, self.state, self.country)

class Settings(BaseModel):
    """Settings table.
       Desc: Stores various settings per tradeshow like mapping, scanType, skipCharacter etc..
    """
    settingType = models.CharField(max_length=100)
    settingName = models.CharField(max_length=100)
    options = models.CharField(max_length=300, null=True, blank=True)

    class Meta:
        db_table = 'Settings'
        
    def __unicode__(self):
        return '%s' % self.settingName
                            
class Tradeshow(BaseModel):    
    """Table for tradeshow.
    """
    name = models.CharField(max_length=100)
    nameCode = models.CharField(max_length=10, blank=True, null=True) # We can define some small code for each Tradeshow Eg. AAAA, AAAB
    sponsors = models.ManyToManyField(Sponsor, blank=True, null=True)
    industry = models.ForeignKey(Industry, blank=True, null=True)
    address = models.ForeignKey(Address)
    startDate = models.DateTimeField()
    endDate = models.DateTimeField()
    email = models.EmailField(blank=True, null=True) # Organizors email.
    contactNo = models.CharField(max_length=30) # Organizors contact number.
    adminPassword = models.CharField(max_length=100) # Password will be required if any settings needed to be changed.
    supportMessage = models.TextField(blank=True, null=True) # Eg. For supoort call xyz..
    website = models.CharField(max_length=300, blank=True, null=True)
    timeZone = models.CharField(max_length=30, blank=True, null=True)
    settings = models.ManyToManyField(Settings, through='TradeshowSettings')
    
    class Meta:
        db_table = 'Tradeshow'

    def __unicode__(self):
        return '%s' % self.name
        
    def _getSponspors(self):
        """
        """
        sponsorNames = [sponsor.name for sponsor in self.sponsors.all()]        
        sponsors = ', '.join(sponsorNames)
        return sponsors

    def _getSettings(self):
        """
        """
        tradeshowSettings = TradeshowSettings.objects.filter(tradeshow=self)
        settings = []
        for tradeshowSetting in tradeshowSettings:            
            data = dict()
            data['settingName'] = tradeshowSetting.setting.settingName
            data['settingType'] = tradeshowSetting.setting.settingType
            data['settingValue'] = tradeshowSetting.settingValue
            data['settingDefaultvalue'] = tradeshowSetting.defaultSettingValue
            data['options'] = tradeshowSetting.setting.options if tradeshowSetting.setting.options else ''
            settings.append(data)
        return settings        
        
    def _getInfo(self):
        """
        """
        info = dict()
        info['tradeshowID'] = self.id
        info['name'] = self.name
        info['nameCode'] = self.nameCode
        info['sponsors'] = self._getSponspors()
        info['industry'] = self.industry.name if self.industry else ''
        info['address'] = str(self.address)
        info['startDate'] = self.startDate
        info['endDate'] = self.endDate
        info['endDate'] = self.endDate
        info['email'] = self.email if self.email else ''
        info['contactNo'] = self.contactNo
        info['adminPassword'] = self.adminPassword        
        info['supportMessage'] = self.supportMessage if self.supportMessage else ''
        info['website'] = self.website if self.website else ''
        info['timeZone'] = self.timeZone if self.timeZone else ''
        return info        
        
class TradeshowSettings(BaseModel):
    """Settings table.
       Desc: Stores various settings per tradeshow like mapping, scanType, skipCharacter etc..
    """
    tradeshow = models.ForeignKey(Tradeshow)
    setting = models.ForeignKey(Settings)        
    settingValue = models.TextField()
    defaultSettingValue = models.CharField(max_length=100, blank=True, null=True)
        
    class Meta:
        db_table = 'TradeshowSettings'

    def __unicode__(self):
        return u'%s|%s|%s' % (self.tradeshow.name, self.setting.settingName, self.settingValue)
        
class Exhibitor(BaseModel):
    """Exhibitor table.
    """
    name = models.CharField(max_length=100)
    email = models.EmailField()
    contactNo = models.CharField(max_length=30)
    alternateEmail = models.EmailField(blank=True, null=True)    
    alternateContactNo = models.CharField(max_length=30, blank=True, null=True)
    address = models.ForeignKey(Address)
    tradeshow = models.ForeignKey(Tradeshow)
    licenseCount = models.IntegerField() # No of licences exibitor has requested.
    #settings = models.ManyToManyField(Settings, through='ExhibitorSettings')
    
    class Meta:
        db_table = 'Exhibitor'

    def __unicode__(self):
        return self.name
        
    def _getInfo(self, includeBooths=False):
        """
        """
        info = dict()
        info['exhibitorID'] = self.id
        info['name'] = self.name
        info['email'] = self.email
        info['contactNo'] = self.contactNo
        info['alternateEmail'] = self.alternateEmail if self.alternateEmail else ''
        info['address'] = str(self.address)
        info['licenseCount'] = self.licenseCount        
        if includeBooths:            
            exhibitorBooths = []
            booths = ExhibitorBooth.objects.filter(exhibitor=self)
            for booth in booths:       
                boothInfo = []         
                boothInfo['name'] = booth.name
                boothInfo['email'] = booth.email
                boothInfo['contactNo'] = booth.contactNo
                boothInfo['boothNo'] = booth.boothNo if booth.boothNo else ''                
                boothInfo['userName'] = booth.userName
                exhibitorBooths.append(boothInfo)                
            info['exhibitorBooths'] = exhibitorBooths        
        return info        

class ExhibitorBooth(BaseModel):
    """ExhibitorBooth table.
       Desc: An exhibitor can have multiple  booths in a tradeshow.An exhibitor can purchase one or more licences.
    """
    userName = models.ForeignKey(UserLogin) # userName provided for this booth.
    exhibitor = models.ForeignKey(Exhibitor)
    name = models.CharField(max_length=100) # For single licence this can be same as exhibitor name
    email = models.EmailField() # For single licence this can be same as exhibitor email
    contactNo = models.CharField(max_length=30) # This can be same as exhibitor in case exhibitor has single booth, otherwise different.
    boothNo = models.CharField(max_length=30, blank=True, null=True) # Booth no in a tradeshow if any.
    
    class Meta:
        db_table = 'ExhibitorBooth'

    def __unicode__(self):
        return self.name

class Fields(BaseModel):
    """Tabel for storing fields.
       Desc: Fields like firstname, lastname, email, contactNo etc.. are created based on the requirement of the tradeshow.
    """
    name = models.CharField(max_length=100)    
    displayName = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'Fields'
        
    def __unicode__(self):
        return '%s' % self.name
        
class Mapping(BaseModel):
    """Table to store mapping for tradeshow.
       Desc: Mappings manages the fields that we need for the tradeshow. Each tradeshow will have only one mapping associated with it.
    """
    tradeshow = models.ForeignKey(Tradeshow)
    totalFields = models.IntegerField()
    badgeIDFieldSeq = models.IntegerField() # Id for the badge
    badgeDataFieldSeq = models.IntegerField() # The filed where the actual data will be stored. Eg badgeData. Akshay$Valsa$akshay@gmail.com$963223
    fields = models.ManyToManyField(Fields, through='FieldsMapping')
    
    class Meta:
        db_table = 'Mapping'

    def __unicode__(self):
        return '%s' % self.tradeshow.name

class FieldsMapping(BaseModel):    
    """Table for storing the mapping of the fields.
       Desc : This table specifies under a particular mapping what fields are stored also stores the fields sequence.
    """
    mapping = models.ForeignKey(Mapping)
    field = models.ForeignKey(Fields)
    fieldSeq = models.IntegerField() # Sequence of the field , can be used when rendering the respcetive fields on the screen.
    isUnique = models.BooleanField() # Specifies the unique field for that mapping.
    
    class Meta:
        db_table = 'FieldsMapping'
        
    def __unicode__(self):
        return u'%s | %s | %s' % (self.mapping.tradeshow.name, self.field.name, self.fieldSeq)
                    
class QualifierType(BaseModel):
    """Table for qualifier types. 
       Desc : Basically a type of a feedback screens Eg basic, advance, Follow up etc..
    """
    qualifierType = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'QualifierType'
        
    def __unicode__(self):
        return '%s' % self.qualifierType

class Question(BaseModel):
    """Question table.    
    """
    question = models.TextField()
    widgetName = models.CharField(max_length=100) # What is the widget type textbox, checkbox , radio etc
    options = models.CharField(max_length=300) # Respective data(coma seperated) as per the widget type. Eg. for field sex : Male,Female
    
    class Meta:
        db_table = 'Question'

    def __unicode__(self):
        return '%s' % self.question
                    
class Qualifier(BaseModel):
    """Qualifier table.
       Desc: Stores the information about a feedback screen. Eg. name, no of questions etc..
    """
    qualifierName = models.CharField(max_length=300)
    qualifierTypeID = models.ForeignKey(QualifierType)    
    screenNo = models.IntegerField()    
    ansFormat = models.IntegerField() 
    totalQuestions = models.IntegerField()
    exhibitor = models.ForeignKey(Exhibitor)
    questions = models.ManyToManyField(Question, through='QualifierQuestions')
    
    class Meta:
        db_table = 'Qualifier'
        
    def __unicode__(self):
        return '%s|%s' % (self.exhibitor.name, self.qualifierName)
        
class QualifierQuestions(BaseModel):
    """QualifierQuestions table.
       Desc: Stores the set of questions for a qualifies definition(feedback screen). 
    """
    qualifier = models.ForeignKey(Qualifier)
    question = models.ForeignKey(Question)
    seq = models.IntegerField() # Sequence of the question in qualifieer screen.
    mapping = models.CharField(max_length=500, null=True, blank=True)
    
    class Meta:
        db_table = 'QualifierQuestions'
        
    def __unicode__(self):
        return u'%s|%s|%s' % (self.qualifier, self.question.question, self.seq)

class LeadMaster(BaseModel):
    """LeadMaster table.
       Desc: Stoes the actual lead information which users will enter via internet or at reception of the tradeshow.
    """
    leadID = models.CharField(max_length=100)
    tradeshow = models.ForeignKey(Tradeshow)
    leadFields = models.ManyToManyField(Fields, through='LeadFields')
    
    class Meta:
        db_table = 'LeadMaster'
        
    def __unicode__(self):
        return '%s' % self.leadID

class LeadFields(BaseModel):
    """Table for storing LeadFields.
       Desc: The number of fields for a tradeshow will vary from tradeshow to tradeshow.
             This table will store the field and values for every lead.  
    """
    lead = models.ForeignKey(LeadMaster)
    field = models.ForeignKey(Fields)
    fieldValue = models.TextField(null=True, blank=True) # Stores actual value of the lead fields like , first name, last name, email etc...

    class Meta:
        db_table = 'LeadFields'
        
    def __unicode__(self):
        return u'%s:%s:%s' % (self.lead.leadID, self.field.name, self.fieldValue)

class DeviceField(models.Model):
    """
    """
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=300)

    def __unicode__(self):
        return u'%s:%s' % (self.name, self.value)

class DeviceDetails(BaseModel):
    """DeviceDetails table.
       Desc: Used to store the details of the device that is used for capturing the leads at respective boths.
    """
    deviceID = models.CharField(max_length=100)
    isActive = models.BooleanField()
    initTime = models.DateTimeField(null=True, blank=True)
    syncTime = models.DateTimeField(null=True, blank=True)
    deviceFields = models.ManyToManyField(DeviceField)

    class Meta:
        db_table = 'DeviceDetails'
        
    def __unicode__(self):
        return '%s' % (self.deviceID)


class LeadDetails(BaseModel):
    """LeadDetails table.
       Desc: Stores the lead details like, capture time, device etc.. 
    """
    #device = models.ForeignKey(DeviceDetails, null=True, blank=True)
    scanType = models.CharField(max_length=100)
    syncID = models.CharField(max_length=100)
    captureTime = models.DateTimeField()
    lookupStatus = models.CharField(max_length=100)
    leadSyncStatus = models.CharField(max_length=100)
    leadType = models.CharField(max_length=100)
    rating = models.IntegerField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'LeadDetails'
        
    def __unicode__(self):
        return '%s' % self.id
        
class Lead(BaseModel):
    """Lead table.
       Desc: Basically a placeholder for lead, which will point to LeadMaster table.
    """
    leadMaster = models.ForeignKey(LeadMaster)
    leadDetails = models.ForeignKey(LeadDetails) # Stores the lead capture and other details.
    exhibitorBooth = models.ForeignKey(ExhibitorBooth) # Maps the lead to respective booth.
    userSession = models.ForeignKey(UserLoginSession, null=True, blank=True)  # Maps the lead to respective user login session.
    answers = models.ManyToManyField(QualifierQuestions, through='Answer')
    
    class Meta:
        db_table = 'Lead'
        
    def __unicode__(self):
        return '%s' % self.leadMaster.leadID
     
    
class Answer(models.Model):
    """Answer table.
       Desc: Table stores the answer provided by the user.
    """
    lead = models.ForeignKey(Lead)
    question = models.ForeignKey(QualifierQuestions)
    answer = models.TextField(null=True, blank=True)
        
    class Meta:
        db_table = 'Answer'
        
    def __unicode__(self):
        return u'%s|%s|%s' % (self.question.id, self.question.question,self.answer)

class ReportUrls(BaseModel):
    """ReportUrls table.
       Desc: Stores the report urls for the tradeshow.
    """
    tradeshow = models.ForeignKey(Tradeshow)
    name = models.CharField(max_length=500)
    url = models.TextField()
    description = models.TextField(null=True, blank=True)
    seq = models.IntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'ReportUrls'
        
    def __unicode__(self):
        return '%s' % self.name

"""
class ExhibitorReportUrls(BaseModel):
    "ExhibitorReportUrls table.Desc: Stroes the report urls for the exhibitor."
   
    exhibitor = models.ForeignKey(Exhibitor)
    reportUrl = models.ForeignKey(ReportUrls)
    name = models.CharField(max_length=500)    
    description = models.TextField(null=True, blank=True)
    seq = models.IntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'ExhibitorReportUrls'
        
    def __unicode__(self):
        return '%s' % self.name
"""

