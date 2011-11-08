# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from OFS.SimpleItem import SimpleItem
from Products.Silva import SilvaPermissions
from Products.Silva.Content import Content
from ZPublisher.BaseRequest import DefaultPublishTraverse
from zExceptions import NotFound

from Products.SilvaMetadata.interfaces import IMetadataService

from silva.app.redirectlink.interfaces import INoPermanentRedirectLink
from silva.app.redirectlink.interfaces import IPermanentRedirectLink
from silva.core import conf as silvaconf
from silva.core.interfaces import ISilvaObject
from silva.core.smi.content import IEditScreen
from silva.ui.rest import PageWithTemplateREST

from five import grok
from zope import component
from zope.container.interfaces import IObjectMovedEvent
from zope.container.interfaces import IObjectAddedEvent, IObjectRemovedEvent
from zope.intid.interfaces import IIntIds
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.traversing.browser import absoluteURL


class PermanentRedirectLink(Content, SimpleItem):
    """Backup link object. This let you keep an reference to a moved
    content and redirect to it.
    """
    meta_type = 'Silva Permanent Redirect Link'
    grok.implements(IPermanentRedirectLink)
    silvaconf.icon('link.png')

    security = ClassSecurityInfo()

    def __init__(self, *args, **kwargs):
        Content.__init__(self, *args, **kwargs)
        self.__target_id = None

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_target')
    def set_target(self, target):
        id_utility = component.getUtility(IIntIds)
        self.__target_id = id_utility.register(target)

    security.declareProtected(
        SilvaPermissions.ReadSilvaContent, 'get_target')
    def get_target(self):
        if self.__target_id is None:
            return None
        id_utility = component.getUtility(IIntIds)
        try:
            return id_utility.getObject(self.__target_id)
        except KeyError:
            return None


InitializeClass(PermanentRedirectLink)


class LinkPublisher(object):
    """Publish a permanent link: do a permanent redirect to new URL.
    """

    def __init__(self, context, request, extra=None):
        self.context = context
        self.request = request
        self.extra = extra

    def render(self):
        """Do the redirect.
        """
        target = self.context.get_target()
        if target is None:
            raise NotFound()
        link = absoluteURL(target, self.request)
        if self.extra is not None:
            link += '/' + '/'.join(self.extra)
        self.request.response.redirect(link, status=301)
        return u''


class LinkPublishContainerTraverse(object):
    """Publish an old path that use to be provided by the moved
    content.
    """
    grok.implements(IBrowserPublisher)

    def __init__(self, context, target):
        self.context = context
        self.current_target = target
        self.extra = []

    def publishTraverse(self, request, name):
        try:
            content = self.current_target.unrestrictedTraverse(name)
            if IPermanentRedirectLink.providedBy(content):
                self.context = content
                self.current_target = content.get_target()
                if self.current_target is None:
                    raise NotFound(name)
                self.extra = []
            else:
                self.current_target = content
                self.extra.append(name)
            return self
        except (NotFound, AttributeError):
            raise NotFound(name)

    def browserDefault(self, request):
        return LinkPublisher(self.context, request, self.extra), ('render',)


class LinkPublishTraverse(DefaultPublishTraverse):
    """Custom traverser for a link. We don't use the default silva one
    not do set caching header on the response.
    """

    def publishTraverse(self, request, name):
        target = self.context.get_target()
        if target is not None:
            try:
                traverser = LinkPublishContainerTraverse(self.context, target)
                return traverser.publishTraverse(request, name)
            except NotFound:
                pass
        return super(LinkPublishTraverse, self).publishTraverse(request, name)

    def browserDefault(self, request):
        return LinkPublisher(self.context, request), ('render',)


class PermanentRedirectEditView(PageWithTemplateREST):
    """Edit view for a permanent link.
    """
    grok.context(IPermanentRedirectLink)
    grok.require('silva.ChangeSilvaContent')
    grok.name('content')
    grok.implements(IEditScreen)

    def update(self):
        target = self.context.get_target()
        self.target_url = None
        if target is not None:
            self.target_url = absoluteURL(target, self.request)
        self.target = target



@grok.subscribe(ISilvaObject, IObjectMovedEvent)
def contentMoved(content, event):
    # We only do if the object is the target of the event.
    if event.object is not content:
        return
    # Don't create a link if it's an add or remove event.
    if IObjectRemovedEvent.providedBy(event) or \
            IObjectAddedEvent.providedBy(event):
        return
    # The content might not want redirect link.
    if INoPermanentRedirectLink.providedBy(content):
        return
    # The extension is not activated.
    if not content.service_extensions.is_installed("silva.app.redirectlink"):
        return
    container = event.oldParent
    factory = container.manage_addProduct['silva.app.redirectlink']
    factory.manage_addPermanentRedirectLink(event.oldName, content.get_title())
    link = getattr(container, event.oldName)
    link.set_target(content)
    binding = component.getUtility(IMetadataService).getMetadata(link)
    binding.setValues('silva-extra', {'hide_from_tocs': 'hide'})
    link.sec_update_last_author_info()
