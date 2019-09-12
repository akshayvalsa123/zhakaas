from django.conf.urls import url

from tsadmin.login_views import LoginView
from tsadmin.login_views import LogoutView
from tsadmin.dashboard_views import DashboardView
from tsadmin.import_views import ImportTradeshowView
from tsadmin.lead_views import LeadsView
from tsadmin.tradeshow_views import getTradeshowExhibitors
from tsadmin.tradeshow_views import getExhibitorLeads
from tsadmin.tradeshow_views import deleteExhibitorLeads
from tsadmin.report_views import TradeshowReportView
from tsadmin.reports import ExhibitorReportView
from tsadmin.reports import DownloadReportView

from tsadmin.es_views import getESMapping
from tsadmin.es_views import saveESMapping
from tsadmin.tradeshow_views import getTradeshowReportUrls
from tsadmin.tradeshow_views import saveTradeshowReportUrls
from tsadmin.export_report_views import ExportReportView
from tsadmin.configure_report_views import ConfigureReportView
#from tsadmin.generate_report_views import GenerateReportView

from tsadmin.csv_reports import downloadCSVReport


urlpatterns = [
    url(r'^login/$', LoginView.as_view()),
    url(r'^logout/$', LogoutView.as_view()),
    url(r'^dashboard/$', DashboardView.as_view()),
    url(r'^import/tradeshow/$', ImportTradeshowView.as_view()),
    url(r'^view/leads/$', LeadsView.as_view()),
    url(r'^get/tradeshow/exhibitors/$', getTradeshowExhibitors),
    url(r'^get/exhibitor/leads/$', getExhibitorLeads),
    url(r'^delete/exhibitor/leads/$', deleteExhibitorLeads),
    url(r'^view/tradeshow/reports/$', TradeshowReportView.as_view()),
    url(r'^view/exhibitor/report/$', ExhibitorReportView.as_view()),
    url(r'^download/exhibitor/report/$', DownloadReportView.as_view()),
    url(r'^download/csv/report/$', downloadCSVReport),

    url(r'^get/es/mapping/$', getESMapping),
    url(r'^save/es/mapping/$', saveESMapping),
    url(r'^export/report/data/$', ExportReportView.as_view()),

    url(r'^configure/report/$', ConfigureReportView.as_view()),
    url(r'^get/tradeshow/report/urls/$', getTradeshowReportUrls),
    url(r'^save/tradeshow/report/urls/$', saveTradeshowReportUrls),
]

