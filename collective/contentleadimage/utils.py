from collective.contentleadimage.interfaces import ILeadImageable
from collective.contentleadimage.config import IMAGE_FIELD_NAME, IMAGE_CAPTION_FIELD_NAME

from plone.indexer import indexer
from zope.component import provideAdapter
from ZODB.POSException import POSKeyError

@indexer(ILeadImageable)
def hasContentLeadImage(obj):
    field = obj.getField(IMAGE_FIELD_NAME)
    
    if field is None:
        if obj.portal_type in ['Image']:
            return False
        field = obj.getField('image')

    if field is not None:
        value = field.get(obj)
        try:
            return not not value
        except POSKeyError:
            # Work around error where we have a field, but we run into
            # a POSKeyError on upgrading Plone.
            return False

provideAdapter(hasContentLeadImage, name='hasContentLeadImage')

def getImageAndCaptionFieldNames(context):

    if context.portal_type in ['News Item', 'FSDPerson']:
        return ('image', 'imageCaption')
    else:
        return (IMAGE_FIELD_NAME, IMAGE_CAPTION_FIELD_NAME)

def getImageAndCaptionFields(context):

    (_IMAGE_FIELD_NAME, _IMAGE_CAPTION_FIELD_NAME) = getImageAndCaptionFieldNames(context)

    if hasattr(context, 'getField'):
        # Use News Item image as Content Lead Image, if it exists
        leadimagefield = context.getField(_IMAGE_FIELD_NAME)
        leadimagecaption = context.getField(_IMAGE_CAPTION_FIELD_NAME)
        
        if leadimagefield and leadimagecaption:
            return (leadimagefield, leadimagecaption)
        elif leadimagefield:
            return (leadimagefield, None)

    return (None, None)
