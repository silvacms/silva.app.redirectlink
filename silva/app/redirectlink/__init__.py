# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.interface import Interface

from silva.core.conf.installer import DefaultInstaller
from silva.core import conf as silvaconf

silvaconf.extensionName("silva.app.redirectlink")
silvaconf.extensionTitle("Silva Permanent Redirect Link")

class IExtension(Interface):
    """Silva Permanent Redirect Link Extension.
    """

install = DefaultInstaller("silva.app.redirectlink", IExtension)

