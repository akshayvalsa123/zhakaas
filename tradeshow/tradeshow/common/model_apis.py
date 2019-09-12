import logging
from api.models import Tradeshow
from api.models import Exhibitor
from api.models import Mapping
from api.models import FieldsMapping

log = logging.getLogger(__name__)

def getTradeshowByID(tradeshowID):
    """
    """
    return _getObjectORNone(Tradeshow, id=tradeshowID)

def getTradeshowByName(tradeshowName):
    """
    """
    return _getObjectORNone(Tradeshow, name=tradeshowName)


def getExhibitorByID(exhibitorID):
    """
    """
    return _getObjectORNone(Exhibitor, id=exhibitorID)

def getExhibitorByName(exhibitorName):
    """
    """
    return _getObjectORNone(Exhibitor, name=exhibitorName)

def getExhibitorBoothByExhibitorID(exhibitorID):
    """
    """
    return _getObjectORNone(ExhibitorBooth, exhibitor=exhibitorID)

def getExhibitorBooths(exhibitor):
    """
    """
    return _getObjectORNone(ExhibitorBooth, exhibitor=exhibitor)

def getExhibitorsByTradeshowID(tradeshowID):
    """
    """
    _exhibitors = Exhibitor.objects.filter(tradeshow=tradeshowID)
    exhibitors = [_exhibitor for _exhibitor in _exhibitors]
    return exhibitors

def getExhibitorsByTradeshowName(tradeshowName):
    """
    """
    _exhibitors = Exhibitor.objects.filter(tradeshow__name=tradeshowName)
    exhibitors = [_exhibitor for _exhibitor in _exhibitors]
    return exhibitors

def getExhibitorsByTradeshow(tradeshow):
    """
    """
    _exhibitors = Exhibitor.objects.filter(tradeshow=tradeshow)
    exhibitors = [_exhibitor for _exhibitor in _exhibitors]
    return exhibitors

def getFieldsMapping(tradeshow):
    """
    """
    mapping = _getObjectORNone(Mapping, tradeshow=tradeshow)
    fieldsMapping = FieldsMapping.objects.filter(mapping=mapping).values('fieldSeq', 'field__name', 'field__displayName', ).order_by('fieldSeq')
    for fieldMapping in fieldsMapping:
        name = fieldMapping['field__name']
        displayName = fieldMapping['field__displayName']
        fieldMapping['fieldName'] = name
        fieldMapping['fieldDisplayName'] = displayName
        del fieldMapping['field__name']
        del fieldMapping['field__displayName']
    # Convert queryset to list
    fieldsMapping = [fieldMapping for fieldMapping in fieldsMapping]
    return fieldsMapping


def _getObjectORNone(model, *args, **kwargs):
    modelName = model.__name__
    try:
        log.info("In _getObjectORNone, Model: [%s] , args: [%s], kwargs: [%s]" % (modelName, args, kwargs))
        modelObj = model.objects.get(*args, **kwargs)
        log.info("In _getObjectORNone, Model [%s], object exists, [%s]" % (modelName, modelObj))
        return modelObj
    except model.DoesNotExist:
        log.info("In _getObjectORNone, Model [%s], object does not exists." % modelName)
        return None
