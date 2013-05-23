# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from zope.interface import Interface

from silva.core.conf.installer import DefaultInstaller
from silva.core import conf as silvaconf

silvaconf.extension_name("silva.app.redirectlink")
silvaconf.extension_title("Silva Permanent Redirect Link")


class IExtension(Interface):
    """Silva Permanent Redirect Link Extension.
    """

class RedirectLinkInstaller(DefaultInstaller):

    def install_custom(self, root):
        # You can't add this content by hand.
        root.add_silva_addable_forbidden('Silva Permanent Redirect Link')


install = RedirectLinkInstaller("silva.app.redirectlink", IExtension)

