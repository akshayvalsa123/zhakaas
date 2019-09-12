from django.conf.urls import url
from api.login_views import LoginView
from api.login_views import LogoutView
from api.lead_views import SyncView
from api.device_views import DeviceSaveView

urlpatterns = [
    url(r'^login/$', LoginView.as_view()),
    url(r'^logout/$', LogoutView.as_view()),
    url(r'^upload/$', SyncView.as_view()),
    url(r'^save/device/info/$', DeviceSaveView.as_view()),
]
