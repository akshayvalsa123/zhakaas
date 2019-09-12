import logging

from django.conf import settings
from django.shortcuts import redirect
from django.views.generic import View
from django.shortcuts import render_to_response

log = logging.getLogger(__name__)

class DashboardView(View):
    """View for dashboard.
    """
    
    def get(self, request):
        """
        """
        log.info("DashboardView:get, requestUser:[%s]" % (request.user))
        if request.user and request.user.is_authenticated():
            return render_to_response("home.html")
        else:
            loginURL = settings.TSADMIN_LOGIN_URL
            log.info("DashboardView:get, User is not logged in so redirecting to login page.")
            return redirect(loginURL)

    

