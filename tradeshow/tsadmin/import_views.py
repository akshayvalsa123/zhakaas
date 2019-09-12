import os
import json
from datetime import datetime
import logging 

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic import View

from tsadmin.forms import ImportTradeshowForm
from tradeshow.common.exceptions import ImportException
from tradeshow.common.utils import _buildResponse
from tradeshow.common import error_codes as errorCodes

from tradeshow.scripts.import_tradeshow import ImportTradeshow

log = logging.getLogger(__name__)

class ImportTradeshowView(View):
    """View for import tradeshow.
    """
    def dispatch(self, request, *args, **kwargs):
        return super(ImportTradeshowView, self).dispatch(request, *args, **kwargs)
    
    def get(self, request):
        """Show the import tradehsow form.
        """
        log.info("ImportTradeshowView:get request")
        form = ImportTradeshowForm()
        return render_to_response('upload.html', {'form': form}, context_instance = RequestContext(request))

    def post(self, request):
        """Import the tradeshow from file.
        """
        log.info("ImportTradeshowView:post request")
        statusCode, message = 0, ''
        try:
            # Get the tradeshow file from request
            form = ImportTradeshowForm(request.POST, request.FILES)
            isValid = form.is_valid()
            log.info("ImportTradeshowView:post, isValid: [%s]" % isValid)        
            if isValid:
                fileName = request.FILES['file'].name
                log.info("ImportTradeshowView:post, fileName: [%s]" % fileName)        
                # Verify the file type
                fileTypes = settings.TRADESHOW_IMPORT_FILE_TYPES
                log.info("ImportTradeshowView:post, Valid FileTypes: [%s]" % fileTypes)        
                _fileName, _fileExt = os.path.splitext(fileName)
                if _fileExt not in fileTypes:
                    _fileTypes = ','.join(fileTypes)
                    statusCode = errorCodes.IMPORT_INVALID_FILETYPE
                    message = "Filetype <b>%s</b> not supported.<br/>Supported Filetypes: <b>%s</b>" % (_fileExt, _fileTypes)
                    raise ImportException(statusCode, message)
                # Import the tradehow file
                result = _saveUploadedFile(fileName, request.FILES['file'])
                log.info("ImportTradeshowView:post, saveUploadedFile result: [%s]" % (result,))
                if not result[0]:
                    statusCode = errorCodes.IMPORT_SAVE_FILE_FAILED
                    message = result[1]
                    raise ImportException(statusCode, message)
                # Send the file for processing
                tradeshowFile = result[1]
                importTradeshow = ImportTradeshow()
                result = importTradeshow.importFromFile(tradeshowFile)
                log.info("ImportTradeshowView:post, result [%s]" % (result, ));
                statusCode, message = result
                if statusCode != 0:
                    raise ImportException(statusCode, message)
                response = _buildResponse(statusCode, message)
                return JsonResponse(response)                
            else:
                statusCode = errorCodes.IMPORT_FORM_INVALID
                # Build the error message from form errors.
                errors = form.errors.as_json()
                errors = json.loads(str(errors))
                log.info("ImportTradeshowView:post, Form Errors: [%s]" % errors)
                all_errors = []
                for error in errors:
                    _errors = errors[error]
                    _message = ';'.join([_error['message'] for _error in _errors])
                    all_errors.append("%s::%s" % (error, _message))
                message = '<br/>'.join(all_errors)
                raise ImportException(statusCode, message)
        except ImportException as ex:
            response = _buildResponse(ex.statusCode, ex.message)
            log.info("ImportTradeshowView:post, ImportException  statusCode: [%s], message: [%s]" % (ex.statusCode, ex.message))        
        except Exception as ex:
            statusCode = errorCodes.IMPORT_EXCEPTION
            message = "Unable to import tradeshow."
            response = _buildResponse(statusCode, message)
            _message = "Exception: %s" % str(ex)
            log.info("ImportTradeshowView:post, Exception  statusCode: [%s], message: [%s]" % (statusCode, _message))
        return JsonResponse(response)

def _saveUploadedFile(fileName, fileHandle):
    """Save the uploaded file to import file location.
    """
    log.info("import_views:_saveUploadedFile, fileName: [%s], fileHandle: [%s]" % (fileName, fileHandle))
    try:
        # Save the file as per the date.
        now = datetime.now()
        dateStr = now.strftime("%Y-%m-%d#%H:%M:%S")
        _fileName, _fileExt = os.path.splitext(fileName)
        dateFileName = "%s##%s%s" % (_fileName, dateStr, _fileExt)
        importLocation = settings.TRADESHOW_IMPORT_LOCATION
        importFile = importLocation + os.sep + dateFileName
        log.info("import_views:_saveUploadedFile, Creating importFile: [%s]" % importFile)
        with open(importFile, 'wb+') as destination:
            for chunk in fileHandle.chunks():
                destination.write(chunk)
        log.info("import_views:_saveUploadedFile, File created successfully.")
        return (True, importFile)
    except Exception as ex:
        log.info("import_views:_saveUploadedFile, Exception: [%s]" % str(ex))
        return (False, "Unable to save uploaded file")
