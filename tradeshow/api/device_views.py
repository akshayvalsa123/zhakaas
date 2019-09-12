import logging
import base64
import json
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.http import JsonResponse
from django.http import HttpResponse
from django.conf import settings as djangoSettings
from django.db import transaction
from api.models import UserLogin
from api.models import UserLoginSession
from api.models import ExhibitorBooth
from api.models import FieldsMapping
from api.models import Qualifier
from api.models import QualifierQuestions
from api.models import DeviceDetails
from api.models import DeviceField
from tradeshow.common import error_codes as errorCodes
from tradeshow.common import model_apis as modelAPIs
from tradeshow.common.utils import _buildResponse
from tradeshow.common.model_apis import _getObjectORNone
from tradeshow.common.exceptions import DeviceSaveException

log = logging.getLogger(__name__)

class DeviceSaveView(View):
    """View for saving Device.
    """
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(DeviceSaveView, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        """
        """
        log.info("DeviceSaveView:post")
        response = dict()
        try:
            postData = json.loads(request.body)
            # Fetch user credentials from request.
            username = postData .get('userName', '').strip()
            authToken = request.META.get('HTTP_X_AUTH_TOKEN', '').strip()
            log.info("DeviceSaveView:post, username/authToken: [%s/%s]" % (username, authToken))
            if not (username and authToken):
                statusCode, message = errorCodes.REQUIRED_PARAMETERS_MISSING, "Username/AuthToken not provided."
                raise DeviceSaveException("Username/AuthToken not provided.")
            # Validate the auth token.
            result = _validateAuthToken(username, authToken)
            log.info("DeviceSaveView:post, _validateAuthToken result: [%s]" % (result, ))
            statusCode, message, userInfo = result
            if statusCode != 0:
                raise DeviceSaveException(statusCode, message)
            # Prpeare the postdata dictionary
            #postData = dict()
            #for key in request.POST:
            #    postData[key] = request.POST[key].strip()
            userLoginSession = userInfo['userSession']
            if userLoginSession.device:
                statusCode = errorCodes.DEVICE_DETAILS_ALREADY_SAVED
                message = "Device details already saved."
                raise DeviceSaveException(statusCode, message)
            result = _saveDeviceInfo(postData, userInfo)
            log.info("DeviceSaveView:post, _saveDeviceInfo result: [%s]" % (result,))
            statusCode, message, saveInfo = result
            if statusCode != 0:
                raise DeviceSaveException(statusCode, message)
            statusCode, message = 0, 'Device saved successfully.'
            _response = _buildResponse(statusCode, message)
        except DeviceSaveException as ex:
            log.info("DeviceSaveView:post, DeviceSaveException, statusCode: [%s], message: [%s]" % (ex.statusCode, ex.message))
            _response = _buildResponse(ex.statusCode, ex.message)
        except Exception as ex:
            log.info("DeviceSaveView:post, Exception: [%s]" % str(ex))
            statusCode = errorCodes.DEVICE_SAVE_VIEW_EXCEPTION
            message = "Unable to save device."
            _response = _buildResponse(statusCode, message)
        return JsonResponse(_response)

def _validateAuthToken(username, authToken):
    """
    """
    try:
        # Validate User Login
        userLogin = _getObjectORNone(UserLogin, userName=username)
        log.info("_validateAuthToken:, UserLogin: [%s]" % userLogin)
        if not userLogin:
            log.info("_validateAuthToken:, Invalid user provided.")
            statusCode, message = errorCodes.USER_NOT_EXISTS, "User not exists."
            raise ValueError("User not exists.")

        # Get the users last login session
        userLoginSession = None
        sessions = UserLoginSession.objects.filter(user=userLogin).order_by('-loginTime')
        sessionCount = sessions.count()
        log.info("_validateAuthToken:, User sessions count: [%s]" % sessionCount)
        if sessionCount:  # user has login sessions
            lastSession = sessions[0]  # get the last session
            log.info("_validateAuthToken:, lastSession/authToken: [%s/%s]" % (lastSession, lastSession.authToken))
            # Check if user is already logged out
            if lastSession.logoutTime:
                log.info("_validateAuthToken:, User already logged out, logoutTime : [%s]" % (lastSession.logoutTime))
                statusCode, message = errorCodes.USER_LOGGED_OUT, "User logged out."
                raise ValueError("User logged out.")
            # Verify the auth token
            if lastSession.authToken != authToken:
                log.info("_validateAuthToken:, Invalid authToken.")
                statusCode, message = errorCodes.INVALID_AUTH_TOKEN, "Invalid authToken provided."
                raise ValueError("Invalid authToken provided.")
            else:
                userLoginSession = lastSession
                log.info("_validateAuthToken: authToken is valid.")
        else:
            log.info("_validateAuthToken:, User is not logged in.")
            statusCode, message = errorCodes.USER_NOT_LOGGED_IN, "User not logged in."
            raise ValueError("User not logged in.")

        if not userLoginSession:
            statusCode, message = errorCodes.NO_USER_LOGIN_SESSION, "User not logged in."
            raise ValueError("User not logged in.")
        status, message = 0, ''
        info = {'userSession': userLoginSession}
        return (status, message, info)
    except ValueError as ex:
        log.info("_validateAuthToken: ValueError, statusCode: [%s], message: [%s]" % (statusCode, message))
        return (statusCode, message, {})
    except Exception as ex:
        log.info("_validateAuthToken: Exception: [%s]" % str(ex))
        statusCode = errorCodes.VALIDATE_AUTH_TOKEN_EXCEPTION
        message = "Unable to validate authToken."
        return (statusCode, message, {})

def _saveDeviceInfo(postData, userInfo):
    """
    """
    try:
        log.info("_saveDeviceInfo: postData: [%s], userInfo:[%s]" % (postData, userInfo))
        userLoginSession = userInfo['userSession']
        deviceFields = postData.get('deviceFields', [])
        fieldInfo = dict()
        for deviceField in deviceFields:
            name = deviceField.get('deviceParameter').strip()
            value = deviceField.get('parameterValue').strip()
            if name and value:
                fieldInfo[name] = value
        log.info("_saveDeviceInfo: fieldInfo : [%s]" % fieldInfo)
        deviceID = fieldInfo.get('deviceID', '').strip()
        log.info("_saveDeviceInfo: fieldInfo deviceID: [%s]" % deviceID)
        if not deviceID:
            log.info("_saveDeviceInfo: generating deviceID")
            deviceID = _generateDeviceID(userLoginSession)
            log.info("_saveDeviceInfo: generated deviceID: [%s]" % deviceID)
            if not deviceID:
                statusCode = errorCodes.GENERATE_DEVICE_ID_FAILED
                message = "Unable to generate deviceID."
                raise ValueError("Unable to generate deviceID.")
        else:
            deviceID = fieldInfo['deviceID']
            del fieldInfo['deviceID']
        with transaction.atomic():
            # Save device details
            deviceDetailsModel = dict()
            deviceDetailsModel['deviceID'] = deviceID
            deviceDetailsModel['isActive'] = True
            deviceDetailsModel['initTime'] = datetime.now()
            log.info("_saveDeviceInfo: deviceDetailsModel: [%s]" % deviceDetailsModel)
            deviceDetails = DeviceDetails(**deviceDetailsModel)
            deviceDetails.save()
            log.info("_saveDeviceInfo: DeviceDetails saved: [%s]" % deviceDetails)
            # Save device fields
            for name in fieldInfo:
                deviceField = DeviceField(name= name, value=fieldInfo[name])
                deviceField.save()
                log.info("_saveDeviceInfo: Created deviceField: [%s]" % deviceField)
                deviceDetails.deviceFields.add(deviceField)
            userLoginSession.device = deviceDetails
            userLoginSession.save()
        statusCode, message = 0, ''
        saveInfo = {'deviceDetails': deviceDetails}
        return (statusCode, message, saveInfo)
    except ValueError as ex:
        log.info("_saveDeviceInfo: ValueError, Exception: [%s]" % (str(ex)))
        return (statusCode, message, {})
    except Exception as ex:
        log.info("_saveDeviceInfo: Exception, Exception: [%s]" % str(ex))
        return (errorCodes.SAVE_DEVICE_EXCEPTION, "Unable to save device info.", {})

def _generateDeviceID(userLoginSession):
    """
    """
    try:
        log.info("_generateDeviceID: userLoginSession: [%s]" % userLoginSession)
        exhibitorBooth = _getObjectORNone(ExhibitorBooth, userName=userLoginSession.user)
        exhibitor = exhibitorBooth.exhibitor
        tradeshow = exhibitor.tradeshow
        key = '%s#%s#%s' % (tradeshow.name, exhibitor.name, exhibitorBooth.userName.userName)
        deviceID = base64.b64encode(key)
        return deviceID
    except Exception as ex:
        log.info("_generateDeviceID: Exception: [%s]" % str(ex))
        return None

