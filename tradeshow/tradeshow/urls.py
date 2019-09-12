from django.conf.urls import include, url
from django.contrib import admin
from api import urls as api_urls
from tsadmin import urls as tsadmin_urls
from django.views.generic import TemplateView

urlpatterns = [
    # Examples:
    # url(r'^$', 'tradeshow.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='index'),
    url(r'^dadmin/', include(admin.site.urls)),
    url(r'^api/', include(api_urls)),
    url(r'^tsadmin/', include(tsadmin_urls)),

    # About pages
    url(r'^about/privacy-policy/$', TemplateView.as_view(template_name='about/privacy.html'),name='privacy'),
    url(r'^about/support/$', TemplateView.as_view(template_name='about/support.html'), name='support'),
    url(r'^demo/$', TemplateView.as_view(template_name='demo/demo.html'), name='demo'),
    url(r'^qrcodes/$', TemplateView.as_view(template_name='qrcodes/qrcodes.html'), name='qrcodes'),
]
