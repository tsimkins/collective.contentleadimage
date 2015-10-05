from AccessControl import Unauthorized
from Acquisition import aq_inner
from zope.component import getUtility
from zope.component import getMultiAdapter
from plone.app.layout.viewlets import ViewletBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from collective.contentleadimage.utils import getImageAndCaptionFields as _getImageAndCaptionFields
from collective.contentleadimage.leadimageprefs import ILeadImagePrefsForm

# We're going to display the lead image first, and then the news item image.
# This gets the news item image out of the body and into the content lead image viewlet
# for standardization purposes.

class LeadImageViewlet(ViewletBase):
    """ A simple viewlet which renders leadimage """

    @property
    def prefs(self):
        portal = getUtility(IPloneSiteRoot)
        return ILeadImagePrefsForm(portal)

    @property
    def full_width(self):

        full_width = False

        context = aq_inner(self.context)

        full_width_field = context.getField('leadimage_full_width')

        if full_width_field:
            full_width = full_width_field.get(context)

        return full_width

    def getImageAndCaptionFields(self):

        context = aq_inner(self.context)

        return _getImageAndCaptionFields(context)

    def caption(self, default=None):
    
        context = aq_inner(self.context)

        (imageField, imageCaptionField) = self.getImageAndCaptionFields()

        imageCaption = ''

        if imageCaptionField:
            imageCaption = str(imageCaptionField.get(context)).strip()

        if default and not imageCaption:
             imageCaption = default

        return imageCaption

    def getImageFieldName(self):
        (imageField, imageCaptionField) = self.getImageAndCaptionFields()
        
        return imageField.getName()        

    def image_sources(self):
        field_name = self.getImageFieldName()

        url = self.context.absolute_url()

        data = []
        
        for (i,j) in [
            ('full-width', 'max-width: 480px'),
        ]:
            data.append({'srcset' : '%s/%s_%s' % (url, field_name, i), 'media' : j})

        return data

    def fullSizeURL(self):
        return '%s/%s_galleryzoom' % (self.context.absolute_url(), self.getImageFieldName())
        
    def bodyTag(self, css_class=''):
        """ returns img tag """

        context = aq_inner(self.context)

        (imageField, imageCaptionField) = self.getImageAndCaptionFields()

        imageCaption = self.caption(default=context.Title())

        if imageField is not None and \
           imageField.get(context) and \
           imageField.get(context).get_size() != 0:

                if self.full_width:
                    scale = "galleryzoom"
                else:
                    scale = self.prefs.body_scale_name
                
                return imageField.tag(context, scale=scale, css_class=css_class,
                                      alt=imageCaption, title=imageCaption)

        return ''


    def render(self):
        context = aq_inner(self.context)
        portal_type = getattr(context, 'portal_type', None)
        
        # Special case for News Item
        if portal_type in self.prefs.allowed_types or portal_type == 'News Item':
            return super(LeadImageViewlet, self).render()
        else:
            return ''


    def getClass(self):

        if self.full_width:
            (imageField, imageCaptionField) = self.getImageAndCaptionFields()
            
            if imageField:
                img = imageField.get(self.context)
                if img:
                    width = img.width
                    # Don't stretch the image if it isn't full-width
                    if width < 650: # Magic number! 
                        return "contentLeadImageContainerLeft"
            
            return "contentLeadImageContainerFullWidth"
        else:
            return "contentLeadImageContainer"

    def allowCrop(self):
        try:
            return self.context.restrictedTraverse('@@crop-image').allowCrop()
        except Unauthorized:
            return False
