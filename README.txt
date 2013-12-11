======================
silva.app.redirectlink
======================

Introduction
============

``silva.app.redirectlink`` is an extension for `Silva`_ 3.0 that lets
you use a new a content type, a redirect link, which does a permanent
HTTP redirect to its target.

You shouldn't add these redirect links to your site manually. They
are automatically created when you move or rename content in Silva.

This lets you preserve old URLs to access moved or renamed contents,
telling the visitor to permanently update its reference to it. This
means search engines will update their search caches with the new
URL of your moved or renamed content. This prevents having content
disappear from search results when it was easily found before.

When you think that visitors and search engines have updated their
references to the moved or renamed contents, you can delete those links
in order to definitively disable all old URLs.

You can keep moving and renaming content items as many times you wish.
The redirect link will keep tracking the content each time it moves
using intids.

For previous version of `Silva`_, look at previous version of
``silva.app.redirectlink``.

Code repository
===============

You can find the code for this extension in Git:
https://github.com/silvacms/silva.app.redirectlink

_ ..Silva: http://silvacms.org
