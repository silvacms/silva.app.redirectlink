# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from silva.core.interfaces import IContent
from zope.interface import Interface


class INoPermanentRedirectLink(Interface):
    """This object can't have a backup link.
    """


class IPermanentRedirectLink(IContent, INoPermanentRedirectLink):
    """A link keep a reference to a moved object. This is use to keep
    the old URL of the object availabe as a permanent http redirect.
    """

    def get_target():
        """Return the target of the link.
        """

    def set_target(target):
        """Set the target of the link.
        """
