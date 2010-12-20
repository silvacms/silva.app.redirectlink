# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.Silva.tests import SilvaTestCase
from Testing.ZopeTestCase.zopedoctest.functional import http

from silva.app.redirectlink.testing import RedirectLinkLayer
import unittest


class ContentCreationTestCase(SilvaTestCase.SilvaTestCase):
    """Test that a redirect link is created each time an object is
    moved if it is installed.
    """
    layer = RedirectLinkLayer

    def afterSetUp(self):
        # XXX: should be author permission
        self.login('manager')

    def test_installation(self):
        """Install the extension, test its installation and
        uninstallation.
        """
        root = self.getRoot()

        # First test installation
        service_extensions = root.service_extensions
        self.failIf(
            service_extensions.is_installed('silva.app.redirectlink'))
        service_extensions.install('silva.app.redirectlink')
        self.failUnless(
            service_extensions.is_installed('silva.app.redirectlink'))

        # Uninstall it
        service_extensions.uninstall('silva.app.redirectlink')
        self.failIf(
            service_extensions.is_installed('silva.app.redirectlink'))

    def test_rename_uninstalled(self):
        """If you rename an object while the extension is not
        installed nothing is done.
        """
        root = self.getRoot()

        # Create some test content
        folder = self.add_folder(root, 'folder', 'Folder')
        document = self.add_document(folder, 'doc', 'Document')
        link = self.add_link(folder, 'link', 'Link', 'http://google.com')
        self.assertListEqual(
            folder.objectIds(), ['doc', 'link',])

        # Rename them
        folder.manage_renameObject('doc', 'renamed_doc')
        self.assertListEqual(
            folder.objectIds(), ['link', 'renamed_doc',])
        self.assertEqual(folder.renamed_doc.meta_type, 'Silva Document')

        folder.manage_renameObject('link', 'renamed_link')
        self.assertListEqual(
            folder.objectIds(), ['renamed_doc', 'renamed_link',])
        self.assertEqual(folder.renamed_link.meta_type, 'Silva Link')

    def test_rename_installed(self):
        """Try to rename an object while the extension is installed.
        """
        root = self.getRoot()
        service_extensions = root.service_extensions
        service_extensions.install('silva.app.redirectlink')

        # Create some test content
        folder = self.add_folder(root, 'folder', 'Folder')
        document = self.add_document(folder, 'doc', 'Document')
        link = self.add_link(folder, 'link', 'Link', 'http://google.com')
        self.assertListEqual(folder.objectIds(), ['doc', 'link',])

        # Rename them
        folder.manage_renameObject('doc', 'renamed_doc')
        self.assertListEqual(
            folder.objectIds(), ['link', 'renamed_doc', 'doc', ])
        self.assertEqual(folder.renamed_doc.meta_type, 'Silva Document')
        self.assertEqual(folder.doc.meta_type, 'Silva Permanent Redirect Link')
        self.assertSame(folder.doc.get_target(), document)
        self.assertEqual(folder.doc.get_title(), document.get_title())

        folder.manage_renameObject('link', 'renamed_link')
        self.assertListEqual(
            folder.objectIds(), ['renamed_doc', 'doc', 'renamed_link', 'link'])
        self.assertEqual(folder.renamed_link.meta_type, 'Silva Link')
        self.assertEqual(folder.link.meta_type, 'Silva Permanent Redirect Link')
        self.assertSame(folder.link.get_target(), link)
        self.assertEqual(folder.link.get_title(), link.get_title())

        # Delete one renamed link
        folder.manage_delObjects(['link',])
        self.assertListEqual(
            folder.objectIds(), ['renamed_doc', 'doc', 'renamed_link',])

    def test_rename_container_install(self):
        """Try to rename a container while the extension is activated.
        """
        root = self.getRoot()
        service_extensions = root.service_extensions
        service_extensions.install('silva.app.redirectlink')

        # Create some test content
        folder = self.add_folder(root, 'folder', 'Folder')
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
        self.assertSame(folder.subfolder.get_target(), subfolder)
        self.assertEqual(folder.subfolder.get_title(), subfolder.get_title())
        self.assertListEqual(subfolder.objectIds(), ['doc', 'other_doc',])

        # And delete
        folder.manage_delObjects(['subfolder',])

    def test_rename_redirectlink(self):
        """We try to rename a permanent redirect link. Nothing should
        happen here.
        """
        root = self.getRoot()
        service_extensions = root.service_extensions
        service_extensions.install('silva.app.redirectlink')

        # Create some test content
        folder = self.add_folder(root, 'folder', 'Folder')
        document = self.add_document(folder, 'doc', 'Document')
        folder.manage_renameObject('doc', 'renamed_doc')
        self.assertEqual(folder.doc.meta_type, 'Silva Permanent Redirect Link')

        # Now rename our link
        folder.manage_renameObject('doc', 'old_doc')
        self.assertListEqual(folder.objectIds(), ['old_doc', 'renamed_doc',])
        self.assertEqual(
            folder.old_doc.meta_type, 'Silva Permanent Redirect Link')


class ContentViewTestCase(SilvaTestCase.SilvaFunctionalTestCase):
    """Test that if you view a redirect link you are well redirect to
    the content element.
    """
    layer = RedirectLinkLayer

    def afterSetUp(self):
        """Create some test data.
        """
        root = self.getRoot()
        service_extensions = root.service_extensions
        service_extensions.install('silva.app.redirectlink')

        # Create some test content
        folder = self.add_folder(root, 'folder', 'Folder')
        document = self.add_document(folder, 'doc', 'Document')
        folder.manage_renameObject('doc', 'renamed_doc')
        self.assertListEqual(folder.objectIds(), ['renamed_doc', 'doc', ])

    def test_content_redirect(self):
        """Viewing one of those objects should redirect you to the new
        one.
        """
        # Access the document
        response = http('GET /root/folder/doc HTTP/1.1')
        self.assertEqual(response.header_output.status, 301)
        self.assertListEqual(
            response.header_output.headers.keys(),
            ['Location', 'Content-Length',])
        self.assertEqual(
            response.getHeader('Location'),
            'http://localhost/root/folder/renamed_doc')
        self.assertEqual(response.getHeader('Content-Length'), '0')

    def test_view_redirect(self):
        """Access a view on a moved content.
        """
        # Access a view on the document
        response = http('GET /root/folder/doc/content.html HTTP/1.1')
        self.assertEqual(response.header_output.status, 301)
        self.assertListEqual(
            response.header_output.headers.keys(),
            ['Location', 'Content-Length',])
        self.assertEqual(
            response.getHeader('Location'),
            'http://localhost/root/folder/renamed_doc/content.html')
        self.assertEqual(response.getHeader('Content-Length'), '0')

    def test_broken_redirect(self):
        """Access a deleted moved content.
        """
        self.root.folder.manage_delObjects(['renamed_doc',])
        response = http('GET /root/folder/doc HTTP/1.1')
        self.assertEqual(response.header_output.status, 404)

    def test_smi(self):
        """Access SMI tabs on a redirect link.
        """
        response = http('GET /root/folder/doc/edit/tab_edit HTTP/1.1')
        self.assertEqual(response.header_output.status, 401)
        response = http('GET /root/folder/doc/edit/tab_metadata HTTP/1.1')
        self.assertEqual(response.header_output.status, 404)
        response = http('GET /root/folder/doc/edit/tab_nonexistant HTTP/1.1')
        self.assertEqual(response.header_output.status, 404)


class ContainerViewTestCase(SilvaTestCase.SilvaFunctionalTestCase):
    """Test that if you view a redirect link you are well redirect to
    the content element if that last on is located inside a moved
    container.
    """
    layer = RedirectLinkLayer

    def afterSetUp(self):
        """Create some test data.
        """
        root = self.getRoot()
        service_extensions = root.service_extensions
        service_extensions.install('silva.app.redirectlink')

        # Create some test content
        folder = self.add_folder(root, 'folder', 'Folder')
        subfolder = self.add_folder(folder, 'subfolder', 'Folder')
        self.add_document(subfolder, 'doc', 'Document')
        self.add_document(subfolder, 'other_doc', 'Other Document')
        folder.manage_renameObject('subfolder', 'data')

    def test_content_redirect(self):
        """Try to access a content in a moved container.
        """
        # Access a content of the moved container
        response = http('GET /root/folder/subfolder/doc HTTP/1.1')
        self.assertEqual(response.header_output.status, 301)
        self.assertListEqual(
            response.header_output.headers.keys(),
            ['Location', 'Content-Length',])
        self.assertEqual(
            response.getHeader('Location'),
            'http://localhost/root/folder/data/doc')
        self.assertEqual(response.getHeader('Content-Length'), '0')

    def test_view_redirect(self):
        """Try to access a view on a content in a moved container
        """
        # Access a view on a content of the moved container
        response = http('GET /root/folder/subfolder/doc/content.html HTTP/1.1')
        self.assertEqual(response.header_output.status, 301)
        self.assertListEqual(
            response.header_output.headers.keys(),
            ['Location', 'Content-Length',])
        self.assertEqual(
            response.getHeader('Location'),
            'http://localhost/root/folder/data/doc/content.html')
        self.assertEqual(response.getHeader('Content-Length'), '0')

    def test_broken_redirect(self):
        """Access a content in a moved deleted container.
        """
        self.root.folder.manage_delObjects(['data',])
        response = http('GET /root/folder/subfolder/doc/content.html HTTP/1.1')
        self.assertEqual(response.header_output.status, 404)

    def test_nonexisting_redirect(self):
        """Try to access a non existing content in a moved container.
        """
        # Access a non-existant content of the moved container
        response = http('GET /root/folder/subfolder/something HTTP/1.1')
        self.assertEqual(response.header_output.status, 404)


class DoubleContainerViewTestCase(SilvaTestCase.SilvaFunctionalTestCase):
    """Test that if you view a redirect link you are well redirect to
    the content element if that last on is located inside two moved
    containers.
    """
    layer = RedirectLinkLayer

    def afterSetUp(self):
        """Create some test content.
        """
        root = self.getRoot()
        service_extensions = root.service_extensions
        service_extensions.install('silva.app.redirectlink')

        # Create some test content
        folder = self.add_folder(root, 'folder', 'Folder')
        subfolder = self.add_folder(folder, 'subfolder', 'Folder')
        self.add_document(subfolder, 'doc', 'Document')
        self.add_document(subfolder, 'other_doc', 'Other Document')
        root.manage_renameObject('folder', 'intern')
        folder.manage_renameObject('subfolder', 'data')

    def test_container_redirect(self):
        """Test redirection in case of a moved content which is inside
        of an another moved content as well.
        """
        # Access a moved moved content.
        response = http('GET /root/folder/subfolder/doc HTTP/1.1')
        self.assertEqual(response.header_output.status, 301)
        self.assertListEqual(
            response.header_output.headers.keys(),
            ['Location', 'Content-Length',])
        self.assertEqual(
            response.getHeader('Location'),
            'http://localhost/root/intern/data/doc')
        self.assertEqual(response.getHeader('Content-Length'), '0')

    def test_view_redirect(self):
        """Try to access a view on a content of a moved container
        inside a another moved content.
        """
        # Access a view on a content of the moved container
        response = http('GET /root/folder/subfolder/doc/content.html HTTP/1.1')
        self.assertEqual(response.header_output.status, 301)
        self.assertListEqual(
            response.header_output.headers.keys(),
            ['Location', 'Content-Length',])
        self.assertEqual(
            response.getHeader('Location'),
            'http://localhost/root/intern/data/doc/content.html')
        self.assertEqual(response.getHeader('Content-Length'), '0')

    def test_broken_redirect(self):
        """Access a content in a moved deleted container in  a moved container.
        """
        self.root.intern.manage_delObjects(['data',])
        response = http('GET /root/folder/subfolder/doc/content.html HTTP/1.1')
        self.assertEqual(response.header_output.status, 404)



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ContentCreationTestCase))
    suite.addTest(unittest.makeSuite(ContentViewTestCase))
    suite.addTest(unittest.makeSuite(ContainerViewTestCase))
    suite.addTest(unittest.makeSuite(DoubleContainerViewTestCase))
    return suite
