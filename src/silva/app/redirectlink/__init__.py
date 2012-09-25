# -*- coding: utf-8 -*-
# Copyright (c) 2010-2012 Infrae. All rights reserved.
# See also LICENSE.txt

from zope.interface import Interface

from silva.core.conf.installer import DefaultInstaller
from silva.core import conf as silvaconf

silvaconf.extensionName("silva.app.redirectlink")
silvaconf.extensionTitle("Silva Permanent Redirect Link")

class IExtension(Interface):
    """Silva Permanent Redirect Link Extension.
    """

install = DefaultInstaller("silva.app.redirectlink", IExtension)

