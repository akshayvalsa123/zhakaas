import logging
import base64
from datetime import datetime
from django.views.generic import View
from django.http import JsonResponse
from django.http import HttpResponse
from django.conf import settings as djangoSettings

from api.models import UserLogin
from api.models import UserLoginSession
from api.models import ExhibitorBooth
from api.models import FieldsMapping
from api.models import Qualifier
from api.models import QualifierQuestions

from tradeshow.common import error_codes as errorCodes
from tradeshow.common import model_apis as modelAPIs
from tradeshow.common.utils import _buildResponse
from tradeshow.common.lead_utils import getLeadsByExhibitorBooth
from tradeshow.common.model_apis import _getObjectORNone
from tradeshow.common.exceptions import LoginException
from tradeshow.common.exceptions import LogoutException

log = logging.getLogger(__name__)

class LoginView(View):
    """View for login.
    """
    
    def get(self, request):
        """
        """
        statusCode = 0
        message = ""
        log.info("LoginView:get")
        response = {}
        try:
            specialLoginCode = djangoSettings.SPECIAL_LOGIN_CODE
            # Fetch user credentials from request.
            username = request.GET.get('username', '').strip()
            password = request.GET.get('password', '').strip()            
            log.info("LoginView:get, username/password: [%s/%s]" % (username, password))
            if not (username and password): 
                raise LoginException(errorCodes.EMPTY_LOGIN_CREDENTIALS, "Username/Password can not be empty.")
            specialLogin = False
            #if username.endswith(specialLoginCode):
            #    username = username[:-len(specialLoginCode)]
            #    specialLogin = True
            #    log.info("LoginView:get, specialLogin is on, username: [%s]" %username)
            # Validate User Login
            userLogin = _getObjectORNone(UserLogin, userName=username, password=password)
            log.info("LoginView:get, userLogin: [%s]" % (userLogin))
            if not userLogin:
                raise LoginException(errorCodes.AUTHENTICATION_FAILED, "User authentication failed.")

            if specialLogin:
                result = self.performSpecialLogin(userLogin)
                status, message = result
                if status != 0:
                    if not message:
                        message = "Special login failed."
                    raise LoginException(errorCodes.SPECIAL_LOGIN_ERROR, message)
            result = self.getAuthToken(userLogin, specialLogin=specialLogin)
            log.info("LoginView:get, getAuthToken, result: [%s]" % (result,))
            status, message, authToken = result
            if status != 0:
                if not message:
                    message = "Unable to get authToken."
                raise LoginException(errorCodes.AUTHTOKEN_ERROR, message)
            response['authToken'] = authToken
            response['loginMessage'] = ''
            if message:
                response['loginMessage'] = message
            # Get the exhibitor booth
            exhibitorBooth = ExhibitorBooth.objects.get(userName=userLogin)            
            log.info("LoginView:get, exhibitorBooth: [%s]" % (exhibitorBooth))

            # Get the exhibitor & tradeshow
            exhibitor = exhibitorBooth.exhibitor
            tradeshow = exhibitor.tradeshow
            log.info("LoginView:get, exhibitor/tradeshow: [%s/%s]" % (exhibitor, tradeshow))
            # Get fields for tradeshow            
            fieldsData = modelAPIs.getFieldsMapping(tradeshow)
            log.info("LoginView:get, fieldsData: [%s]" % (fieldsData))
            fields = dict()
            fields['data'] = fieldsData
            fields['total'] = len(fieldsData)
            response['fields'] = fields

            # Get tradeshow settings         
            settingsData = tradeshow._getSettings()
            log.info("LoginView:get, settingsData: [%s]" % (settingsData))
            settings = dict()
            settings['data'] = settingsData
            settings['total'] = len(settingsData)
            response['settings'] = settings

            # Get tradeshow qualifiers for exhibitor        
            qualifierTypes = dict()
            exhibitorQualifiers = Qualifier.objects.filter(exhibitor=exhibitor)
            log.info("LoginView:get, exhibitorQualifiers: [%s]" % (exhibitorQualifiers))
            for exhibitorQualifier in exhibitorQualifiers:
                data = dict()
                # Get the qualifier screen information
                qualifierType = exhibitorQualifier.qualifierTypeID.qualifierType
                data['qualifierName'] =  exhibitorQualifier.qualifierName
                data['screenNo'] = exhibitorQualifier.screenNo
                data['totalQuestions'] = exhibitorQualifier.totalQuestions
                # Get the qualifier screen questions
                questionsData = []
                questions = exhibitorQualifier.questions.order_by('QualifierQuestions.seq')
                for question in questions:
                    questionInfo = dict()   
                    questionInfo['question'] = question.question
                    questionInfo['widget'] = question.widgetName
                    questionInfo['option'] = question.options
                    # TODO : Calling QualifierQuestions can be avoided.
                    qualifierQuestion = QualifierQuestions.objects.get(qualifier=exhibitorQualifier, question=question)
                    questionInfo['seq'] = qualifierQuestion.seq
                    questionInfo['qualifierQuestionID'] = qualifierQuestion.id
                    questionsData.append(questionInfo)
                data['questions'] = questionsData            
                qualifierTypes.setdefault(qualifierType, []).append(data)            
            # Prepare the qualifiers data
            qualifiersData = []
            for qualifierType in qualifierTypes:
                qualifierInfo = dict()
                qualifierInfo['qualifierType'] = qualifierType
                qualifierInfo['total'] = len(qualifierTypes[qualifierType])
                qualifierInfo['data'] = qualifierTypes[qualifierType]
                qualifiersData.append(qualifierInfo)
            log.info("LoginView:get, qualifiersData: [%s]" % qualifiersData)
            qualifiers = dict()    
            qualifiers['data'] = qualifiersData
            qualifiers['total'] = len(qualifiersData)
            response['qualifiers'] = qualifiers        
            response['tradeshowInfo'] = tradeshow._getInfo()
            response['exhibitorInfo'] = exhibitor._getInfo()
	    response['leads'] = getLeadsByExhibitorBooth(exhibitorBooth)
            _response = _buildResponse(0, '', response)
        except LoginException as ex:
            log.info("LoginView:get, LoginException, statusCode: [%s], message: [%s]" % (ex.statusCode, ex.message))           
            _response = _buildResponse(ex.statusCode, ex.message)
        except Exception as ex:
            log.info("LoginView:get, Exception: [%s]" % str(ex))           
            statusCode = errorCodes.LOGIN_VIEW_EXCEPTION
            message = "Unable to login."
            _response = _buildResponse(statusCode, message)
            raise ex
        return JsonResponse(_response)
    
    def getAuthToken(self, userLogin, specialLogin=False):
        """
        """
        statusCode = 0
        message = ''
        log.info("LoginView:getAuthToken, userLogin: [%s], specialLogin: [%s]" % (userLogin, specialLogin))
        try:
            # Get the users last login session
            sessions = UserLoginSession.objects.filter(user=userLogin).order_by('-loginTime')
            sessionCount = sessions.count()
            log.info("LoginView:getAuthToken, User sessions count: [%s]" % sessionCount)
            if sessionCount: # user has login sessions
                lastSession = sessions[0] # get the last session
                log.info("LoginView:getAuthToken, lastSession: [%s]" % lastSession)
                if not lastSession.logoutTime: # Last session is not yet logged out
                    log.info("LoginView:getAuthToken, User already logged in , so will perform logout.")
                    # logout the user
                    logoutTime = datetime.now()
                    lastSession.logoutTime = logoutTime
                    lastSession.comment = "Logging out existing session for new login request."
                    lastSession.save()
                    log.info("LoginView:getAuthToken, User logged out, lastSession: [%s]" % lastSession)
                    message = "Login successful, however had to logout previous logged in session for user '%s'" % lastSession.user.userName
            # Create the login session
            loginTime = datetime.now()
            loginKey = "%s:%s" % (userLogin.userName, loginTime)
            log.info("LoginView:getAuthToken, loginKey: [%s]" % loginKey)
            authToken = base64.b64encode(loginKey)
            log.info("LoginView:getAuthToken, authToken: [%s]" % authToken)
            sessionObj = UserLoginSession(user=userLogin, loginTime=loginTime, authToken=authToken, specialLogin=specialLogin)
            sessionObj.save()
            log.info("LoginView:getAuthToken, sessionObj: [%s]" % sessionObj)
            return (statusCode, message, authToken)
        except Exception as ex:
            statusCode = -1
            log.info("LoginView:getAuthToken, Exception: [%s]" % str(ex))
            return (statusCode, message, '')

    def performSpecialLogin(self, userLogin):
        """
        """
        statusCode = 0
        message = ''
        log.info("LoginView:performSpecialLogin, userLogin: [%s]" % (userLogin))
        try:
            # Get the users last login session
            sessions = UserLoginSession.objects.filter(user=userLogin).order_by('-loginTime')
            sessionCount = sessions.count()
            log.info("LoginView:performSpecialLogin, User sessions count: [%s]" % sessionCount)
            if sessionCount: # user has login sessions
                lastSession = sessions[0] # get the last session
                log.info("LoginView:performSpecialLogin, lastSession: [%s]" % lastSession)
                if lastSession.logoutTime: # Last session is already logged out
                    # TODO: should raise exception, however not to confuse the user will continue with the login.
                    log.info("LoginView:performSpecialLogin, Special login not required as the last session is logged out.")
                    return (statusCode, 'Special login not required as the last session is logged out.We will create new session and continue.') 
                else:
                    log.info("LoginView:performSpecialLogin, User not logged out, so will perform logout.")
                    # logout the user
                    logoutTime = datetime.now()
                    lastSession.logoutTime = logoutTime
                    lastSession.comment = "Logging out to perform special login"
                    lastSession.save()
                    log.info("LoginView:performSpecialLogin, User logged out, lastSession: [%s]" % lastSession)
                    return (statusCode, 'Logging out to perform special login') 
            else:
                # TODO: should raise exception, however not to confuse the user will continue with the login.
                log.info("LoginView:performSpecialLogin, Special login not required as user is not yet logged in.")
                return (statusCode, 'Special login not required as user is not yet logged in.') 
        except Exception as ex:
            statusCode = -1
            message = "Unable to perform special login."
            log.info("LoginView:performSpecialLogin, Exception: [%s]" % str(ex))
            return (statusCode, message)

class LogoutView(View):
    """View for logout.
    """
    def get(self, request):
        """
        """
        statusCode = 0
        message = ""
        log.info("LogoutView:get")
        response = {}
        
        try:
            # Fetch user credentials from request.
            username = request.GET.get('username', '').strip()
            authToken = request.META.get('HTTP_X_AUTH_TOKEN', '').strip()
            log.info("Authtoken: [%s]" % authToken)
            log.info("LogoutView:get, username/authToken: [%s/%s]" % (username, authToken))
            if not (username and authToken):
                raise LogoutException(errorCodes.MISSING_LOGOUT_CREDENTIALS, "Username/AuthToken not provided.")

            # Validate User Login
            userLogin = _getObjectORNone(UserLogin, userName=username)
            log.info("LogoutView:get, UserLogin: [%s]" % userLogin)
            if not userLogin:
                log.info("LogoutView:get, Invalid user provided.")
                raise LogoutException(errorCodes.USER_NOT_EXISTS, "User not exists.")

            # Get the users last login session
            now = datetime.now()
            userLoginSession = None
            sessions = UserLoginSession.objects.filter(user=userLogin).order_by('-loginTime')
            sessionCount = sessions.count()
            log.info("LogoutView:get, User sessions count: [%s]" % sessionCount)
            if sessionCount: # user has login sessions
                lastSession = sessions[0] # get the last session
                log.info("LogoutView:get, lastSession/authToken: [%s/%s]" % (lastSession, lastSession.authToken))
                # Check if user is already logged out
                if lastSession.logoutTime:
                    log.info("LogoutView:get, User already logged out, logoutTime : [%s]" % (lastSession.logoutTime))
                    response = dict()
                    _response = _buildResponse(0, 'Old session, User Logout successful.', response)
                    return JsonResponse(_response)
                    #raise LogoutException(errorCodes.USER_LOGGED_OUT, "User already logged out.")
                # Verify the auth token
                if lastSession.authToken != authToken:
                    try:
                        oldSession = UserLoginSession.get.objects(user=userLogin, authToken=authToken)                        
                        if oldSession.logoutTime:
                            log.info("LogoutView:get, oldSession, User already logged out, logoutTime : [%s]" % (oldSession.logoutTime))
                            response = dict()
                            _response = _buildResponse(0, 'Old session, User already logged out.', response)
                            return JsonResponse(_response)
                        else:
                            log.info("LogoutView:get, oldSession, User not logged out yet")
                            oldSession.logoutTime = now
                            oldSession.save()
                            log.info("LogoutView:get, oldSession, User logout successful.")
                            response = dict()
                            _response = _buildResponse(0, 'Old session, User Logout successful.', response)
                            return JsonResponse(_response)
                    except Exception as ex:
                        log.info("LogoutView:get, oldSession, Exception: [%s]" % str(ex))
                        _response = _buildResponse(0, 'Old session, User Logout Exception.', response)
                        return JsonResponse(_response)
                    log.info("LogoutView:get, Invalid authToken.")
                    raise LogoutException(errorCodes.INVALID_AUTH_TOKEN, "Invalid authToken provided.")
                else:
                    userLoginSession = lastSession
                    log.info("LogoutView:get, User will be logged out.")
            else:
                log.info("LogoutView:get, User does not have any old login sessions.")
                _response = _buildResponse(0, 'User not logged in.', {})
                return JsonResponse(_response)
                #raise LogoutException(errorCodes.USER_NOT_LOGGED_IN, "User not logged in.")

            if not userLoginSession:
                log.info("LogoutView:get, Unable to get user login session.")
                _response = _buildResponse(0, 'User not logged in.', {})
                return JsonResponse(_response)
                #raise LogoutException(errorCodes.NO_USER_LOGIN_SESSION, "User not logged in.")
            # Save the logout time.
            userLoginSession.logoutTime = now
            userLoginSession.save()
            log.info("LogoutView:get, User logout successful.")
            response = dict()
            _response = _buildResponse(0, 'User Logout successful.', response)
        except LogoutException as ex:
            log.info("LoginView:get, LogoutException, statusCode: [%s], message: [%s]" % (ex.statusCode, ex.message))           
            _response = _buildResponse(ex.statusCode, ex.message)
        except Exception as ex:
            log.info("LogoutView:get, Exception: [%s]" % str(ex))           
            statusCode = errorCodes.LOGOUT_VIEW_EXCEPTION
            message = "Unable to logout."
            _response = _buildResponse(statusCode, message)            
        return JsonResponse(_response)

