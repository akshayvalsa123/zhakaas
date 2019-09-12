import logging
import logging.handlers
import csv
from api.models import Address
csvFile = "/home/rohit/Desktop/sync/Exibition/ImportCSVs/tshow.csv"

# Initialise Logger
log = logging.getLogger(__name__)
#hdlr = logging.StreamHandler()
hdlr = logging.FileHandler('/tmp/load_tradeshow.log')
#hdlr = logging.handlers.RotatingFileHandler('/tmp/logs/add_artifact_creatorID.log', maxBytes=10*1024*1024, backupCount=500)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
log.addHandler(hdlr)
log.setLevel(logging.INFO)

class LoadTradeshow:
    """Class to prepare entry for Tradeshow.
    """
    
    def __init__(self, tradeshowCsvFile):
        """
        """
        self.addressFields = ['address1', 'street', 'city', 'state', 'country', 'zipcode']
        self.tradeshowCsvFile = tradeshowCsvFile
        self.errors = []
        self.warnings = []
        self.tradeshowInfo = dict()
        self.addressInfo = dict()
        self.fieldsInfo = dict()
    
    def process(self):
        """
        """
        # Load the csv file
        self.processTradeshowCsvFile()
        if self.errors:        
            return self._displayErrors()
        log.info("Saving address for tradeshow.")
        self._saveAddress(self.addressInfo)
        
    def _saveAddress(self, addressInfo):
        """
        """
        log.info("In _saveAddress, addressInfo: [%s]" % addressInfo)
        # Prepare address
        for addressField in self.addressFields:
            if not addressInfo.get(addressField):
                log.info("Mandatory field %s can not be blank" % addressField)
                self.errors.append("Mandatory field %s can not be blank" % addressField)
        if self.errors:        
            return self._displayErrors()
        else:
            try:
                address = Address(**addressInfo)
                addressObj = Address.objects.filter(**addressInfo)
                if addressObj:
                    pass
                
                #address.save()
                log.info("Successfully saved address")
            except Exception as ex:
                log.info("Error in saving address. Error: [%s]" % str(ex))
                return
        
    def _displayErrors(self):
        """
        """
        log.info("============== Got Errors ==============")
        for error in self.errors:
            log.info("Error: [%s]" % error)
        log.info("========================================")            
        
        
    def processTradeshowCsvFile(self):
        """
        """
        isHeader = True
        with open(self.tradeshowCsvFile, 'rb') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in csvreader:
                log.info("Processing row: [%s]" % row)
                if isHeader:
                    isHeader = False
                    continue            
                tradeshowFieldName = row[0].strip() 
                if tradeshowFieldName:
                    tradeshowFieldValue = row[1].strip()
                    if tradeshowFieldName.endswith('*'): 
                        if tradeshowFieldValue:
                            self.tradeshowInfo[tradeshowFieldName[:-1]] = tradeshowFieldValue
                        else:
                            log.info("Tradeshow field %s can not be blank." % tradeshowFieldName)
                            self.errors.append("Tradeshow field %s can not be blank." % tradeshowFieldName)
                    else:
                        self.tradeshowInfo[tradeshowFieldName] = tradeshowFieldValue
                try:
                    addressFieldName = row[2].strip() 
                    if addressFieldName:
                        addressFieldValue = row[3].strip()
                        if addressFieldName.endswith('*'):
                            if addressFieldValue:
                                self.addressInfo[addressFieldName[:-1]] = addressFieldValue
                            else:                        
                                log.info("Address field %s can not be blank." % addressFieldName)
                                self.errors.append("Address field %s can not be blank." % addressFieldName)
                        else:
                            self.addressInfo[addressFieldName] = addressFieldValue
                except Exception as ex:
                    log.info("Error in processing address.")
                try:
                    fieldName = row[4].strip()
                    fieldSeq = row[5].strip()
                    if fieldName:
                        if fieldSeq:
                            self.fieldsInfo[fieldName] = fieldSeq
                        else:
                            log.info("fieldSeq can not be empty, FieldName: [%s]" % fieldName)
                            self.errors.append("fieldSeq can not be empty, FieldName: [%s]" % fieldName)
                except Exception as ex:
                    log.info("Error in processing fields.")

obj = LoadTradeshow(csvFile)
obj.process()
