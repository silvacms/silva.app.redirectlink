# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.Silva.Content import Content
from Products.Silva import SilvaPermissions
from OFS.SimpleItem import SimpleItem

from silva.app.redirectlink import interfaces
from silva.core import conf as silvaconf
from silva.core.views import views as silvaviews
from silva.core.interfaces import ISilvaObject

from five import grok
from zope import component
from zope.app.container.interfaces import IObjectMovedEvent
from zope.app.container.interfaces import IObjectAddedEvent, IObjectRemovedEvent
from zope.app.intid.interfaces import IIntIds


class PermanentRedirectLink(Content, SimpleItem):
    """Backup link object. This let you keep an reference to a moved
    content and redirect to it.
    """
    meta_type = 'Silva Permanent Redirect Link'
    grok.implements(interfaces.IPermanentRedirectLink)
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
        return id_utility.getObject(self.__target_id)

    def is_deletable(self):
        # You can always delete this content.
        return 1

InitializeClass(PermanentRedirectLink)


class PermanentRedirectLinkView(silvaviews.View):
    """View for a backup link: to a permanent redirect.
    """

    grok.context(interfaces.IPermanentRedirectLink)

    def render(self):
        target = self.context.get_target()
        if target is not None:
            link = target.absolute_url()
            # We do a permanent redirect
            self.response.redirect(link, status=301)
            return 'Redirecting to <a href="%s">%s</a>' % (link, link)
        return ''


class BackupEditView(silvaviews.SMIView):
    """Edit view for a backup link.
    """

    grok.context(interfaces.IPermanentRedirectLink)
    grok.name(u'tab_edit')

    def render(self):
        target = self.context.get_target()
        if target is not None:
            link = target.absolute_url() + '/edit/tab_edit'
            self.response.redirect(link)
            return 'Redirecting to <a href="%s">%s</a>' % (link, link)
        return ''


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
    if interfaces.INoPermanentRedirectLink.providedBy(content):
        return
    # The extension is not activated.
    if not content.service_extensions.is_installed("silva.app.redirectlink"):
        return
    container = event.oldParent
    factory = container.manage_addProduct['silva.app.redirectlink']
    factory.manage_addPermanentRedirectLink(event.oldName, content.get_title())
    link = getattr(container, event.oldName)
    link.set_target(content)
    link.sec_update_last_author_info()
