# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

import silva.app.redirectlink
from silva.core.interfaces import IPublicationWorkflow
from zope.component import getUtility
from Products.SilvaMetadata.interfaces import IMetadataService
from Products.Silva.testing import SilvaLayer


class RedirectLinkTestCase(unittest.TestCase):
    layer = SilvaLayer(silva.app.redirectlink)

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('author')

    def add_folder(self, root, identifier, title):
        factory = root.manage_addProduct['Silva']
        factory.manage_addFolder(identifier, title)
        return getattr(root, identifier)

    def add_link(self, root, identifier, title):
        factory = root.manage_addProduct['Silva']
        factory.manage_addLink(identifier, title)
        link = getattr(root, identifier)

        self.layer.login('editor')
        IPublicationWorkflow(link).publish()
        self.layer.login('author')

        return link

    def add_document(self, root, identifier, title):
        factory = root.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent(identifier, title)
        mock = getattr(root, identifier)

        self.layer.login('editor')
        IPublicationWorkflow(mock).publish()
        self.layer.login('author')

        return mock


class ContentCreationTestCase(RedirectLinkTestCase):
    """Test that a redirect link is created each time an object is
    moved if it is installed.
    """

    def test_installation(self):
        """Install the extension, test its installation and
        uninstallation.
        """
        # First test installation
        service_extensions = self.root.service_extensions
        is_installed = service_extensions.is_installed
        self.assertFalse(is_installed('silva.app.redirectlink'))
        service_extensions.install('silva.app.redirectlink')
        self.assertTrue(is_installed('silva.app.redirectlink'))

        # Uninstall it
        service_extensions.uninstall('silva.app.redirectlink')
        self.assertFalse(is_installed('silva.app.redirectlink'))

    def test_rename_uninstalled(self):
        """If you rename an object while the extension is not
        installed nothing is done.
        """
        # Create some test content
        folder = self.add_folder(self.root, 'folder', 'Folder')
        self.add_document(folder, 'doc', 'Document')
        self.add_link(folder, 'link', 'Link')

        self.assertListEqual(
            folder.objectIds(), ['doc', 'link',])

        # Rename them
        folder.manage_renameObject('doc', 'renamed_doc')
        self.assertListEqual(
            folder.objectIds(), ['link', 'renamed_doc',])
        self.assertEqual(folder.renamed_doc.meta_type,
            'Mockup VersionedContent')

        folder.manage_renameObject('link', 'renamed_link')
        self.assertListEqual(
            folder.objectIds(), ['renamed_doc', 'renamed_link',])
        self.assertEqual(folder.renamed_link.meta_type, 'Silva Link')

    def test_rename_installed(self):
        """Try to rename an object while the extension is installed.
        """
        service_extensions = self.root.service_extensions
        service_extensions.install('silva.app.redirectlink')

        # Create some test content
        folder = self.add_folder(self.root, 'folder', 'Folder')
        document = self.add_document(folder, 'doc', 'Document')
        link = self.add_link(folder, 'link', 'Link')
        self.assertListEqual(folder.objectIds(), ['doc', 'link',])

        # Rename them
        folder.manage_renameObject('doc', 'renamed_doc')
        self.assertListEqual(
            folder.objectIds(), ['link', 'renamed_doc', 'doc', ])
        self.assertEqual(
            folder.renamed_doc.meta_type, 'Mockup VersionedContent')
        self.assertEqual(folder.doc.meta_type, 'Silva Permanent Redirect Link')
        self.assertEqual(folder.doc.get_target(), document)
        self.assertEqual(folder.doc.get_title(), document.get_title())

        folder.manage_renameObject('link', 'renamed_link')
        self.assertListEqual(
            folder.objectIds(), ['renamed_doc', 'doc', 'renamed_link', 'link'])
        self.assertEqual(folder.renamed_link.meta_type, 'Silva Link')
        self.assertEqual(folder.link.meta_type, 'Silva Permanent Redirect Link')
        self.assertEqual(folder.link.get_target(), link)
        self.assertEqual(folder.link.get_title(), link.get_title())

        # Delete one renamed link
        folder.manage_delObjects(['link',])
        self.assertListEqual(
            folder.objectIds(), ['renamed_doc', 'doc', 'renamed_link',])

    def test_rename_container_install(self):
        """Try to rename a container while the extension is activated.
        """
        get_metadata = getUtility(IMetadataService).getMetadataValue
        service_extensions = self.root.service_extensions
        service_extensions.install('silva.app.redirectlink')

        # Create some test content
        folder = self.add_folder(self.root, 'folder', 'Folder')
        subfolder = self.add_folder(folder, 'subfolder', 'Folder')
        self.add_document(subfolder, 'doc', 'Document')
        self.add_document(subfolder, 'other_doc', 'Other Document')
        self.assertListEqual(folder.objectIds(), ['subfolder',])
        self.assertListEqual(subfolder.objectIds(), ['doc', 'other_doc',])

        # Rename
        folder.manage_renameObject('subfolder', 'data')
        self.assertListEqual(folder.objectIds(), ['data', 'subfolder',])
        self.assertEqual(folder.data.meta_type, 'Silva Folder')
        self.assertEqual(
            folder.subfolder.meta_type, 'Silva Permanent Redirect Link')
        self.assertEqual(folder.subfolder.get_target(), subfolder)
        self.assertEqual(folder.subfolder.get_title(), subfolder.get_title())
        self.assertListEqual(subfolder.objectIds(), ['doc', 'other_doc',])
        self.assertEqual(
            get_metadata(folder.subfolder, 'silva-settings', 'hide_from_tocs'),
            'hide')

        # And delete
        folder.manage_delObjects(['subfolder',])

    def test_rename_redirectlink(self):
        """We try to rename a permanent redirect link. Nothing should
        happen here.
        """
        service_extensions = self.root.service_extensions
        service_extensions.install('silva.app.redirectlink')

        # Create some test content
        folder = self.add_folder(self.root, 'folder', 'Folder')
        self.add_document(folder, 'doc', 'Document')

        folder.manage_renameObject('doc', 'renamed_doc')
        self.assertEqual(folder.doc.meta_type, 'Silva Permanent Redirect Link')

        # Now rename our link
        folder.manage_renameObject('doc', 'old_doc')
        self.assertEqual(set(folder.objectIds()),
            set(['old_doc', 'renamed_doc']))
        self.assertEqual(
            folder.old_doc.meta_type, 'Silva Permanent Redirect Link')


class ContentViewTestCase(RedirectLinkTestCase):
    """Test that if you view a redirect link you are well redirect to
    the content element.
    """

    def setUp(self):
        """Create some test data.
        """
        super(ContentViewTestCase, self).setUp()
        service_extensions = self.root.service_extensions
        service_extensions.install('silva.app.redirectlink')

        # Create some test content
        folder = self.add_folder(self.root, 'folder', 'Folder')
        self.add_document(folder, 'doc', 'Document')

        folder.manage_renameObject('doc', 'renamed_doc')
        self.assertListEqual(folder.objectIds(), ['renamed_doc', 'doc', ])

    def test_content_redirect(self):
        """Viewing one of those objects should redirect you to the new
        one.
        """
        # Access the document
        browser = self.layer.get_browser()
        browser.options.follow_redirect = False
        status = browser.open('/root/folder/doc')
        self.assertEqual(301, status)
        self.assertEqual(
            browser.headers['Location'],
            'http://localhost/root/folder/renamed_doc')
        self.assertEqual(browser.headers['Content-Length'], '0')

    def test_view_redirect(self):
        """Access a view on a moved content.
        """
        # Access a view on the document
        browser = self.layer.get_browser()
        browser.options.follow_redirect = False
        status = browser.open('/root/folder/doc/content.html')
        self.assertEqual(301, status)
        self.assertEqual(
            browser.headers['Location'],
            'http://localhost/root/folder/renamed_doc/content.html')
        self.assertEqual(browser.headers['Content-Length'], '0')

    def test_broken_redirect(self):
        """Access a deleted moved content.
        """
        self.root.folder.manage_delObjects(['renamed_doc',])
        browser = self.layer.get_browser()
        status = browser.open('/root/folder/doc')
        self.assertEqual(status, 404)

    def test_smi(self):
        """Access SMI tabs on a redirect link.
        """
        raise AssertionError('needs selenium')
        # response = http(
        #     'GET /root/folder/doc/edit/tab_edit HTTP/1.1', parsed=True)
        # self.assertEqual(response.getStatus(), 401)
        # response = http(
        #     'GET /root/folder/doc/edit/tab_metadata HTTP/1.1', parsed=True)
        # self.assertEqual(response.getStatus(), 401)
        # response = http(
        #     'GET /root/folder/doc/edit/tab_nonexistant HTTP/1.1',
        #     handle_errors=True, parsed=True)
        # self.assertEqual(response.getStatus(), 404)


class ContainerViewTestCase(RedirectLinkTestCase):
    """Test that if you view a redirect link you are well redirect to
    the content element if that last on is located inside a moved
    container.
    """

    def setUp(self):
        """Create some test data.
        """
        super(ContainerViewTestCase, self).setUp()
        service_extensions = self.root.service_extensions
        service_extensions.install('silva.app.redirectlink')

        # Create some test content
        folder = self.add_folder(self.root, 'folder', 'Folder')
        subfolder = self.add_folder(folder, 'subfolder', 'Folder')
        self.add_document(subfolder, 'doc', 'Document')
        self.add_document(subfolder, 'other_doc', 'Other Document')
        folder.manage_renameObject('subfolder', 'data')

    def test_content_redirect(self):
        """Try to access a content in a moved container.
        """
        # Access a content of the moved container
        browser = self.layer.get_browser()
        browser.options.follow_redirect = False
        status = browser.open('/root/folder/subfolder/doc')
        self.assertEqual(301, status)
        self.assertEqual(
            browser.headers['Location'],
            'http://localhost/root/folder/data/doc')
        self.assertEqual(browser.headers['Content-Length'], '0')

    def test_view_redirect(self):
        """Try to access a view on a content in a moved container
        """
        # Access a view on a content of the moved container
        browser = self.layer.get_browser()
        browser.options.follow_redirect = False
        status = browser.open('/root/folder/subfolder/doc/content.html')
        self.assertEqual(301, status)
        self.assertEqual(
            browser.headers['Location'],
            'http://localhost/root/folder/data/doc/content.html')
        self.assertEqual(browser.headers['Content-Length'], '0')

    def test_broken_redirect(self):
        """Access a content in a moved deleted container.
        """
        self.root.folder.manage_delObjects(['data',])
        browser = self.layer.get_browser()
        status = browser.open('/root/folder/subfolder/doc/content.html')
        self.assertEqual(status, 404)

    def test_nonexisting_redirect(self):
        """Try to access a non existing content in a moved container.
        """
        # Access a non-existant content of the moved container
        browser = self.layer.get_browser()
        status = browser.open('/root/folder/subfolder/something')
        self.assertEqual(404, status)


class DoubleContainerViewTestCase(RedirectLinkTestCase):
    """Test that if you view a redirect link you are well redirect to
    the content element if that last on is located inside two moved
    containers.
    """

    def setUp(self):
        """Create some test content.
        """
        super(DoubleContainerViewTestCase, self).setUp()
        service_extensions = self.root.service_extensions
        service_extensions.install('silva.app.redirectlink')

        # Create some test content
        folder = self.add_folder(self.root, 'folder', 'Folder')
        subfolder = self.add_folder(folder, 'subfolder', 'Folder')
        self.add_document(subfolder, 'doc', 'Document')
        self.add_document(subfolder, 'other_doc', 'Other Document')
        self.root.manage_renameObject('folder', 'intern')
        folder.manage_renameObject('subfolder', 'data')

    def test_container_redirect(self):
        """Test redirection in case of a moved content which is inside
        of an another moved content as well.
        """
        browser = self.layer.get_browser()
        browser.options.follow_redirect = False
        # Access a moved moved content.
        status = browser.open('/root/folder/subfolder/doc')
        self.assertEqual(301, status)
        self.assertEqual(
            browser.headers['Location'],
            'http://localhost/root/intern/data/doc')
        self.assertEqual(browser.headers['Content-Length'], '0')

    def test_view_redirect(self):
        """Try to access a view on a content of a moved container
        inside a another moved content.
        """
        # Access a view on a content of the moved container
        browser = self.layer.get_browser()
        browser.options.follow_redirect = False
        browser.options.handle_errors = False
        status = browser.open('/root/intern/data/doc/content.html')
        self.assertEqual(200, status)
        status = browser.open('/root/folder/subfolder/doc/content.html')
        self.assertEqual(301, status)
        self.assertEqual(
            browser.headers['Location'],
            'http://localhost/root/intern/data/doc/content.html')
        self.assertEqual(browser.headers['Content-Length'], '0')

    def test_broken_redirect(self):
        """Access a content in a moved deleted container in  a moved container.
        """
        self.root.intern.manage_delObjects(['data',])
        browser = self.layer.get_browser()
        status = browser.open('/root/folder/subfolder/doc/content.html')
        self.assertEqual(404, status)



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ContentCreationTestCase))
    suite.addTest(unittest.makeSuite(ContentViewTestCase))
    suite.addTest(unittest.makeSuite(ContainerViewTestCase))
    suite.addTest(unittest.makeSuite(DoubleContainerViewTestCase))
    return suite
