from django.contrib import admin

# Register your models here.

from api.models import UserLogin
from api.models import Sponsor
from api.models import Industry
from api.models import Address
from api.models import Tradeshow
from api.models import Settings
from api.models import Exhibitor
from api.models import ExhibitorBooth
from api.models import Fields
from api.models import Mapping
from api.models import QualifierType
from api.models import Question
from api.models import Qualifier
from api.models import LeadMaster
from api.models import LeadFields
from api.models import DeviceDetails
from api.models import LeadDetails
from api.models import Lead
from api.models import Answer
from api.models import FieldsMapping
from api.models import TradeshowSettings
from api.models import QualifierQuestions
from api.models import ReportUrls
from api.models import UserLoginSession


admin.site.register(UserLogin)
admin.site.register(Sponsor)
admin.site.register(Industry)
admin.site.register(Address)
admin.site.register(Tradeshow)
admin.site.register(Settings)
admin.site.register(Exhibitor)
admin.site.register(ExhibitorBooth)
admin.site.register(Fields)
admin.site.register(Mapping)
admin.site.register(QualifierType)
admin.site.register(Question)
admin.site.register(Qualifier)
admin.site.register(LeadMaster)
admin.site.register(LeadFields)
admin.site.register(DeviceDetails)
admin.site.register(LeadDetails)
admin.site.register(Lead)
admin.site.register(Answer)
admin.site.register(FieldsMapping)
admin.site.register(TradeshowSettings)
admin.site.register(QualifierQuestions)
admin.site.register(UserLoginSession)


class FieldsAdmin(admin.ModelAdmin):
    fields = ('name', 'displayName')

class ReportsAdmin(admin.ModelAdmin):
    list_display = ('name', 'seq', 'id')

admin.site.register(ReportUrls, ReportsAdmin)
