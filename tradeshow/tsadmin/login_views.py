import logging
from django.conf import settings
from django.shortcuts import redirect
from django.views.generic import View
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.template import RequestContext
from tradeshow.common import error_codes as errorCodes
from tradeshow.common.utils import _buildResponse
from django.http import JsonResponse

log = logging.getLogger(__name__)

class LoginView(View):
    """View for login.
    """
    
    def get(self, request):
        """
        """
        log.info("LoginView:get, requestUser:[%s]" % (request.user))
        if request.user and request.user.is_authenticated():
            redirectURL = settings.TSADMIN_LOGIN_REDIRECT_URL
            log.info("LoginView:get, User is logged in so redirecting to Dashboard page.")
            return redirect(redirectURL)
        return render_to_response("login.html", context_instance = RequestContext(request))

    def post(self, request):
        """
        """
        statusCode , message = 0, ""
        try:
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '').strip()
            log.info("LoginView:post, username:[%s], password:[%s]" % (username, password))
            if not (username and password):
                statusCode, message = errorCodes.EMPTY_LOGIN_CREDENTIALS, "username/password can not be empty."
                raise ValueError(message)
            user = authenticate(username=username, password=password)
            log.info("LoginView:post, user:[%s]" % (user))
            if user is not None:
                # the password verified for the user
                if user.is_active:
                    log.info("LoginView:post, User is valid, active and authenticated")
                    loginInfo = {'redirectURL': settings.TSADMIN_LOGIN_REDIRECT_URL}
                    response = _buildResponse(statusCode, message, moreInfo=loginInfo)
                    login(request, user)
                    log.info("LoginView:post, Redirecting to url: [%s]" % settings.TSADMIN_LOGIN_REDIRECT_URL)
                else:
                    log.info("LoginView:post, The password is valid, but the account has been disabled!")
                    statusCode = errorCodes.USER_DISABLED
                    message = "User has been disabled."
                    raise ValueError(message)
            else:
                # the authentication system was unable to verify the username and password
                log.info("LoginView:post, The username and password were incorrect")
                statusCode = errorCodes.INVALID_LOGIN_CREDENTIALS
                message = "The username and password were incorrect."
                raise ValueError(message)
        except ValueError as ex:
            log.info("LoginView:post ValueError, statusCode: [%s], Message: [%s]" % (statusCode, message))
            response =_buildResponse(statusCode, message)
        except Exception as ex:
            log.info("LoginView:post Exception, Exception: [%s]" % str(ex))
            statusCode = errorCodes.TSADMIN_LOGIN_EXCEPTION
            message = "Unable to login."
            response = _buildResponse(statusCode, message)
        return JsonResponse(response)


class LogoutView(View):
    """View for logout.
    """

    def get(self, request):
        """
        """
        log.info("LogoutView:get, requestUser:[%s]" % (request.user))
        logout(request)
        log.info("LogoutView:get, Logout successful.")
        loginURL = settings.TSADMIN_LOGIN_URL
        log.info("LogoutView:get, loginURL: [%s]" % loginURL)
        log.info("LogoutView:get, User is logged out now redirecting to login page.")
        return redirect(loginURL)

