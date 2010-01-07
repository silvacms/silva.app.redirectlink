# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.interface import Interface

from silva.core.conf.installer import DefaultInstaller
from silva.core import conf as silvaconf

silvaconf.extensionName("SilvaBackupLink")
silvaconf.extensionTitle("Silva Backup Link")

class IExtension(Interface):
    """Silva Backup Link Extension.
    """

install = DefaultInstaller("SilvaBackupLink", IExtension)

