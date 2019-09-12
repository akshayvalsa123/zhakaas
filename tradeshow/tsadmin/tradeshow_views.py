import logging
import traceback
from django.http import JsonResponse

from django.db import transaction

from django.shortcuts import render_to_response
from api.models import Tradeshow
from api.models import ExhibitorBooth
from api.models import Lead
from api.models import LeadFields
from api.models import LeadMaster
from api.models import LeadDetails
from api.models import ReportUrls
from tradeshow.common import model_apis as modelAPI
from tradeshow.common import error_codes as errorCodes
from tradeshow.common.utils import _buildResponse
from tradeshow.common.utils import _buildDataTableEmptyResponse
from tradeshow.common.utils import _buildResponse
from tradeshow.common.model_apis import _getObjectORNone
from django.http import JsonResponse

log = logging.getLogger(__name__)

def getTradeshowExhibitors(request):
    """Get the exhibitor for the tradeshow.
    """
    response = {}
    tradeshowID = request.GET.get('tradeshowID', '').strip()
    if not tradeshowID:
        statusCode = -1
        message = "tradeshowID not provided."
        response = _buildResponse(statusCode, message)
        return JsonResponse(response)

    _exhibitors = modelAPI.getExhibitorsByTradeshowID(tradeshowID)
    exhibitors = [(_exhibitor.id, _exhibitor.name) for _exhibitor in _exhibitors]
    response = _buildResponse(0, "", {'exhibitors': exhibitors})
    return JsonResponse(response)

def getExhibitorLeads(request):
    """Get the exhibitor leads.
    """
    try:
        draw = request.GET.get('draw', 1)
        # Get tradeshow and exhibitor
        tradeshowID = request.GET.get('tradeshowID', '').strip()
        tradeshow = modelAPI.getTradeshowByID(tradeshowID)
        if not tradeshow:
            statusCode = errorCodes.TRADESHOW_NOT_EXISTS 
            message = "Unable to get tradeshow."
            raise LeadException(statusCode, message)
        log.info("getExhibitorLeads: tradeshow: [%s]" % tradeshow)
        exhibitorID = request.GET.get('exhibitorID', '').strip()
        exhibitor = modelAPI.getExhibitorByID(exhibitorID)
        if not exhibitor:
            statusCode = errorCodes.EXHIBITOR_NOT_EXISTS 
            message = "Unable to get exhibitor."
            raise LeadException(statusCode, message, draw)
        log.info("getExhibitorLeads: exhibitor: [%s]" % exhibitor)
        try:
            start = int(request.GET['start'])
            pageSize = int(request.GET['length'])
        except:
            start, pageSize = 1, 10

        log.info("getExhibitorLeads: start/pageSize : [%s/%s]" % (start, pageSize))
        # Get fields mapping
        fieldsMapping = modelAPI.getFieldsMapping(tradeshow)
        if not fieldsMapping:
            statusCode = errorCodes.FIELDS_NOT_AVAILABLE
            message = "Unable to get fields."
            raise LeadException(statusCode, message, draw)          
        log.info("getExhibitorLeads: fieldsMapping : [%s]" % (fieldsMapping))

        count = 0
        fieldRows = []        
        exhibitorBooths = ExhibitorBooth.objects.filter(exhibitor=exhibitor)
        leads = Lead.objects.filter(exhibitorBooth__in = exhibitorBooths)
        totalRecords = leads.count()        
        log.info("getExhibitorLeads: ExhibitorLeadCount: [%s]" % (totalRecords))
        leadInfoList = []
        for lead in leads[start:(start+pageSize)]:
            fields = {}
            count += 1
            # Get the lead fields
            leadMaster = lead.leadMaster            
            leadFields = LeadFields.objects.filter(lead=leadMaster)
            for leadField in leadFields:
                fields[leadField.field.name] = leadField.fieldValue
            # Prepar the lead fields row
            fieldsList = []
            fieldRow = [lead.id]
            for fieldMapping in fieldsMapping:
                name = fieldMapping['fieldName']
                if name == 'badgeData':
                    continue
                value = fields[name]
                if name in ['firstName', 'lastName', 'name']:
                    value = value.title()
                fieldRow.append(value)        
            fieldRows.append(fieldRow)

        response = dict()
        response['draw'] = draw
        response['recordsTotal'] = totalRecords
        response['recordsFiltered'] = totalRecords
        response['data'] = fieldRows
        log.info("getExhibitorLeads: response: [%s]" % response)
        return JsonResponse(response)
    except LeadException as ex:
        response = _buildDataTableEmptyResponse(ex.statusCode, ex.message)
        log.info("getExhibitorLeads: LeadException statusCode: [%s], Message: [%s]" % (ex.statusCode, ex.message))
    except Exception as ex:
        statusCode = errorCodes.GET_EXHIBITOR_LEADS_EXCEPTION
        message = "Unable to get exhibitor leads"
        response = _buildDataTableEmptyResponse(statusCode, message)
        log.info("getExhibitorLeads: Exception statusCode: [%s], Error: [%s]" % (statusCode, str(ex)))
    return JsonResponse(response)

def deleteExhibitorLeads(request):
    """
    """
    response = {}
    try:
        log.info("deleteExhibitorLeads:get")
        mandatoryFields = ['tradeshowID', 'exhibitorID', 'deleteType']
        for mandatoryField in mandatoryFields:
            field = request.POST.get(mandatoryField)
            if not field:
                statusCode = FIELD_IS_MANDATORY
                message = '%s, is mandatory' % mandatoryField
                raise LeadException(message)
                
        # Get all the fields
        tradeshowID = request.POST['tradeshowID']
        exhibitorID = request.POST['exhibitorID']
        deleteType = request.POST['deleteType']
        selectedIDs = request.POST.get('selectedIDs', '')
        log.info("deleteExhibitorLeads: tradeshowID/exhibitorID/deleteType/selectedIDs: [%s/%s/%s/%s]" % (tradeshowID, exhibitorID, deleteType, selectedIDs))

        tradeshow = modelAPI.getTradeshowByID(tradeshowID)
        if not tradeshow:
            statusCode = errorCodes.TRADESHOW_NOT_EXISTS 
            message = "Unable to get tradeshow."
            raise LeadException(statusCode, message)
        log.info("deleteExhibitorLeads: tradeshow: [%s]" % tradeshow)
        exhibitor = modelAPI.getExhibitorByID(exhibitorID)
        if not exhibitor:
            statusCode = errorCodes.EXHIBITOR_NOT_EXISTS 
            message = "Unable to get exhibitor."
            raise LeadException(statusCode, message)
        log.info("deleteExhibitorLeads: exhibitor: [%s]" % exhibitor)
        if deleteType not in ['selected', 'all']:
            statusCode = errorCodes.INVALID_DELETE_TYPE
            message = 'Invalid delete type.'
            raise LeadException(statusCode, message)

        if deleteType == 'all': # Get all the leads
            log.info("deleteExhibitorLeads: Deleting all the leads for the tradeshow: [%s]" % tradeshow)
            exhibitorBooths = ExhibitorBooth.objects.filter(exhibitor=exhibitor)
            leads = Lead.objects.filter(exhibitorBooth__in = exhibitorBooths).values_list('leadMaster', 'leadDetails')
        else: # Get the selected leads
            selectedIDs = selectedIDs.split(',')
            selectedIDs = [x.strip() for x in selectedIDs]
            selectedIDs = filter(None, selectedIDs)
            if not selectedIDs:
                statusCode = errorCodes.LEAD_NOT_SELECTED
                message = 'Lead not selected.'
                raise LeadException(statusCode, message)
            log.info("deleteExhibitorLeads:, selectedIDs: [%s]" % selectedIDs)
            log.info("deleteExhibitorLeads: Deleting selected leads for the tradeshow: [%s]" % tradeshow)
            selectedIDs = [int(_id) for _id in selectedIDs]
            leads = Lead.objects.filter(id__in = selectedIDs).values_list('leadMaster', 'leadDetails')
        leadMasterIDs = filter(None, [x[0] for x in leads])
        leadDetailsIDs = filter(None, [x[1] for x in leads])
        with transaction.atomic():
            log.info("deleteExhibitorLeads: deleting [%s] LeadMasters." % len(leadMasterIDs))
            log.info("deleteExhibitorLeads: deleting [%s] LeadDetails." % len(leadDetailsIDs))
            deleteMasterRsults = LeadMaster.objects.filter(id__in=leadMasterIDs).delete()
            log.info('deleteExhibitorLeads: deleteMasterRsults: [%s]' % deleteMasterRsults)
            deleteDetailsResults = LeadDetails.objects.filter(id__in=leadDetailsIDs).delete()
            log.info('deleteExhibitorLeads: deleteDetailsResults: [%s]' % deleteDetailsResults)
            statusCode = 0
            message = 'Leads deleted successfully.'
            response =_buildResponse(statusCode, message)
            return JsonResponse(response)
    except LeadException as ex:
        log.info("deleteExhibitorLeads: LeadException, statusCode: [%s], Message: [%s]" % (ex.statusCode, ex.message))
        response =_buildResponse(ex.statusCode, ex.message)
    except Exception as ex:
        log.info("deleteExhibitorLeads: Exception, Exception: [%s]" % str(ex))
        statusCode = errorCodes.DELETE_EXHIBITOR_LEADS_EXCEPTION
        message = "Unable to delete leads."
        response =_buildResponse(statusCode, message)
        import traceback
        log.info("Error :%s" % traceback.format_exc());

    return JsonResponse(response)

def getTradeshowReportUrls(request):
    """Get the tradeshow report urls.
    """
    try:
        response = {}
        tradeshowID = request.GET.get('tradeshowID', '').strip()
        tradeshow = _getObjectORNone(Tradeshow, id=tradeshowID)
        log.info("getTradeshowReportUrls: tradeshow: [%s]" % tradeshow)
        if not tradeshow:
            statusCode = -1
            message = "Tradeshow not exists."
            raise ValueError(message)
        reportUrls = ReportUrls.objects.filter(tradeshow=tradeshow).order_by('seq')
        log.info("getTradeshowReportUrls: reportUrls: [%s]" % reportUrls)
        _reportUrls = [reportUrl for reportUrl in reportUrls]        
        emptyReportUrl = {'name':'', 'url': '', 'description': '', 'seq':'', 'id': 0}
        emptyReportUrls = []
        for i in range(10):
            _reportUrls.append(emptyReportUrl)        
        return render_to_response("report_urls.html", {'reportUrls': _reportUrls})
    except ValueError as ex:
        log.info("getTradeshowReportUrls: ValueError: [%s]" % str(ex))
        return render_to_response("report_urls.html", {'errorMessage': message, 'reportUrls': []})
    except Exception as ex:
        log.info("getTradeshowReportUrls: Exception: [%s]" % str(ex))
        message = "Unable to get report urls."
        return render_to_response("report_urls.html", {'errorMessage': message, 'reportUrls': []})

def saveTradeshowReportUrls(request):
    """
    """
    try:
        postData = {}
        tradeshowID = request.POST.get('tradeshowID', '').strip()
        tradeshow = _getObjectORNone(Tradeshow, id=tradeshowID)
        log.info("saveTradeshowReportUrls: tradeshow: [%s]" % tradeshow)
        if not tradeshow:
            status = -1
            message = "Tradeshow not exists."
            raise ValueError(message)

        for key in request.POST:
            postData[key] = request.POST[key]
        log.info("saveTradeshowReportUrls: postData: [%s]" % postData)
        result = _saveTradeshowReportUrls(tradeshow, postData)
        log.info("saveTradeshowReportUrls: _saveTradeshowReportUrls, result: [%s]" % (result, ))
        status, message = result
        if status != 0:
            raise ValueError(message)
        status, message = 0, 'Report Urls saved successfully.'
    except ValueError as ex:
        log.info("saveTradeshowReportUrls: ValueError: [%s]" % str(ex))
    except Exception as ex:
        log.info("saveTradeshowReportUrls: Exception: [%s]" % str(ex))
        status = -1
        message = "Exception in saving report urls."

    response =_buildResponse(status, message)
    return JsonResponse(response)

def _saveTradeshowReportUrls(tradeshow, postData):
    """
    """
    try:
        # Get the max index , no of rows of report Urls
        indices = set()
        for key in postData:
            # ids are like name_1, seq_1
            if key.split('_')[0] not in ['id', 'name', 'seq', 'url', 'description']:
                continue
            index = key.split('_')[1]
            indices.add(int(index))
        indices = list(indices)
        indices.sort()
        maxIndex = indices[-1]
        log.info("_saveTradeshowReportUrls: maxIndex: [%s]" % maxIndex)
        deleteIDs = []
        with transaction.atomic():
            # Iterate through each row of reportURL
            for index in range(1, maxIndex+1):
                _id =  postData.get('id_%s' % index, '0').strip()
                name = postData.get('name_%s' % index, '').strip()
                seq = postData.get('seq_%s' % index, '').strip()
                url = postData.get('url_%s' % index, '').strip()
                description = postData.get('description_%s' % index, '').strip()
                log.info("_saveTradeshowReportUrls: id/name/seq/url/description : [%s/%s/%s/%s/%s]" % (_id, name, seq, url, description))
                _id = int(_id)
                if _id > 0: # This will be existing reportURL
                    log.info("_saveTradeshowReportUrls: reportURL exists: ID:[%s]" % _id)
                    if not (name and seq and url and description): # In case row is empty means reportUrls needs to be deleted.
                        log.info("_saveTradeshowReportUrls: reportURL will be deleted for ID:[%s]" % _id)
                        deleteIDs.append(_id)
                        continue
                else:# This will be new reportURL
                    log.info("_saveTradeshowReportUrls: reportURL not exists: ID:[%s]" % _id)
                    if not (name or seq or url or description):  # handle empty row
                        continue
                if not (name and seq and url):
                    log.info("_saveTradeshowReportUrls: Mandatory fields Name, Seq and URL not present for ID:[%s]" % _id)
                    raise Exception("Name, Seq and URL are mandatory.")
                reportUrlModel = dict()
                reportUrlModel['tradeshow'] = tradeshow
                reportUrlModel['name'] = name
                reportUrlModel['seq'] = int(seq)
                reportUrlModel['url'] = url
                if description:
                    reportUrlModel['description'] = description
                if _id > 0:
                    reportUrlModel['id'] = _id
                log.info("_saveTradeshowReportUrls: reportUrlModel:[%s]" % reportUrlModel)
                reportUrl = ReportUrls(**reportUrlModel)        
                reportUrl.save()
                log.info("_saveTradeshowReportUrls: Saved reportUrl:[%s]" % reportUrl)

            if deleteIDs:
                log.info("_saveTradeshowReportUrls: Deleting reportUrls, deleteIDs:[%s]" % deleteIDs)
                deleteResult = ReportUrls.objects.filter(id__in=deleteIDs).delete()
                log.info("_saveTradeshowReportUrls: deleteResult:[%s]" % (deleteResult,))
        status, message = 0, "ReportUrls saved successfully."
        return (status, message)
    except Exception as ex:
        status, message = -1, "Unable to save report urls."
        log.info("saveTradeshowReportUrls: Exception: [%s]" % traceback.format_exc())
        return (status, message)
