import logging
from datetime import datetime
from django.conf import settings
from elasticsearch import Elasticsearch
from tsadmin.es_data import getTradeshowESData

log = logging.getLogger(__name__)

def getTradeshowIndexInfo(tradeshowName):
    """
    """
    try:
        es_host = settings.ES_HOST
        _tradeshowName = tradeshowName.replace(' ', '_').lower()
        #index_name = "2017-09-03_%s" % _tradeshow
        es = Elasticsearch([es_host])    
        log.info("getTradeshowIndex: es: [%s]" % es)
        if not es.ping():
            return (False, 'ES not running.')    
        
        index_query = '*%s' % _tradeshowName
        _indices = es.indices.get(index_query)  
        indexNames = _indices.keys()
        log.info("getTradeshowIndex: indexNames: [%s]" % indexNames)
        if not indexNames:
            return (True, 'No index created for tradeshow, %s.' % tradeshowName)    

        indexDates = []
        for indexName in indexNames:
            log.info("getTradeshowIndex: indexName: [%s]" % indexName)
            try:
                _indexDate = indexName.split('_')[0]
                dt = datetime.strptime(_indexDate, '%Y-%m-%d')            
                indexDates.append(dt)
            except Exception as ex:
                log.info("getTradeshowIndex: indexName format is not valid, Error: [%s]" % str(ex))
        if indexDates:
            indexDates.sort(reverse=True)
            indexDate = indexDates[0]
            indexName = '%s-%s-%s_%s' % (indexDate.year, indexDate.month, indexDate.day, _tradeshowName)
            countInfo = es.count(indexName)
            leadCount = countInfo['count']
            return (True, 'Last index is %s with lead count %s' % (indexName, leadCount))    
        else:
            return (True, 'No index created for tradeshow, %s.' % tradeshowName)
    except Exception as ex:
        log.info("getTradeshowIndex:  Exception: [%s]" % str(ex))
        return (False, 'Unable to get Tradeshow index info.')

def getESStatus():
    """
    """
    try:
        es_host = settings.ES_HOST
        es = Elasticsearch([es_host])    
        log.info("getESStatus: es: [%s]" % es)
        esStatus = es.ping()
        log.info("getESStatus:  esStatus: [%s]" % esStatus)
        return esStatus
    except Exception as ex:
        log.info("getESStatus:  Exception: [%s]" % str(ex))
        return False

def exportToES(tradeshowID):
    """
    """
    try:
        exhibitorID = 'all'
        result = getTradeshowESData(tradeshowID, exhibitorID)
        log.info("exportToES: result: [%s]" % (result, ))
        status, message, exhibitorLeads = result
        if status != 0:
            return (status, message)
        if not exhibitorLeads:
            log.info("exportToES: No data available.")
            status, message = -1, "No data available"
            return (status, message)

        tradeshowName = exhibitorLeads[0]['tradeshow']
        log.info("exportToES: tradeshowName: [%s]" % tradeshowName)
        _tradeshowName = tradeshowName.replace(' ', '_').lower()
    	today = datetime.today()	
        indexName = "%s-%s-%s_%s" % (today.year, today.month, today.day, _tradeshowName)
        # index_name = "2017-09-03_%s" % _tradeshow
        log.info("exportToES: indexName: [%s]" % indexName)
        es_host = settings.ES_HOST
        es = Elasticsearch([es_host])
        log.info("exportToES: es: [%s]" % es)
        # Delete existing indices

        #result = es.indices.delete(index=indexName, ignore=[400, 404])
        #log.info("exportToES: Deleted the index: [%s], result: [%s]" % (indexName, result))
        #result = es.indices.create(index=indexName, ignore=400)	
        #log.info("exportToES: Created the index: [%s], result: [%s]" % (indexName, result))

        totalLeadCount = 0
        for exhibitorLead in exhibitorLeads:
            leads = exhibitorLead['leads']
            exhibitor = exhibitorLead['exhibitor']
            log.info("exportToES: exhibitor: [%s]" % exhibitor)            
            docType = exhibitor.replace(' ', '_').upper()
            log.info("exportToES: docType: [%s]" % docType)    
            leadCount = 0
            for lead in leads:
                leadCount += 1
                totalLeadCount += 1
                captureTime = datetime.strptime(lead['captureTime'], settings.TRADESHOW_TIME_FORMAT)
                lead['captureTime'] = captureTime
                log.info("exportToES: lead: [%s]" % lead)    
                result = es.index(indexName, docType, body=lead)
                #result = 'DONE'
                log.info("exportToES: es.index result: [%s]" % result)    
            log.info("exportToES: Exhibitor: [%s], LeadCount: [%s]" % (exhibitor, leadCount))    
        log.info("exportToES: Total lead count: [%s]" % (totalLeadCount))    
        return (0, 'Export to ES Successful.')
    except Exception as ex:
        log.info("getTradeshowIndex:  Exception: [%s]" % str(ex))
        return (-1, 'Unable to get Tradeshow index info.')
