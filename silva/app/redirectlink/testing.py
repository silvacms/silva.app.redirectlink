# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.Five import zcml
from Products.Silva.tests import SilvaTestCase
from Testing.ZopeTestCase import installPackage


class RedirectLinkLayer(SilvaTestCase.SilvaLayer):
    """Setup the silva.app.redirectlink.
    """

    @classmethod
    def setUp(self):
        # Load our ZCML, which add the extension as a Product
        from silva.app import redirectlink
        zcml.load_config('configure.zcml', redirectlink)

        installPackage('silva.app.redirectlink')
