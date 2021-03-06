"""
content.py: routes related to content

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from bottle import request, redirect
from bottle_utils.ajax import roca_view
from bottle_utils.html import set_qparam, urlunquote
from bottle_utils.i18n import i18n_url

from librarian_content.decorators import with_meta
from librarian_content.library import metadata
from librarian_core.contrib.cache.decorators import cached
from librarian_core.contrib.templates.renderer import template
from librarian_ui.paginator import Paginator

from ..helpers import open_archive


@cached(prefix='content', timeout=300)
def content_count(query, lang, content_type):
    archive = open_archive()
    return archive.get_count(query, lang, content_type)


@cached(prefix='content', timeout=300)
def filter_content(query, lang, content_type, offset, limit):
    archive = open_archive()
    raw_metas = archive.get_content(terms=query,
                                    lang=lang,
                                    content_type=content_type,
                                    offset=offset,
                                    limit=limit)
    return [metadata.Meta(request.app.supervisor, meta['path'], data=meta)
            for meta in raw_metas]


@roca_view('library/content_list', 'library/_content_list', template_func=template)
def content_list():
    """ Show list of content """
    # parse search query
    query = urlunquote(request.params.get('q', '')).strip()
    # parse language filter
    default_lang = request.user.options.get('content_language', None)
    lang = request.params.get('language', default_lang)
    request.user.options['content_language'] = lang
    # parse content type filter
    content_type = request.params.get('content_type')
    if content_type not in metadata.CONTENT_TYPES:
        content_type = None
    # parse pagination params
    page = Paginator.parse_page(request.params)
    per_page = Paginator.parse_per_page(request.params)
    # get content list filtered by above parsed filter params
    item_count = content_count(query, lang, content_type)
    pager = Paginator(item_count, page, per_page)
    offset, limit = pager.items
    metas = filter_content(query,
                           lang,
                           content_type,
                           offset=offset,
                           limit=limit)
    return dict(metadata=metas,
                pager=pager,
                vals=request.params.decode(),
                query=query,
                chosen_lang=lang,
                content_types=metadata.CONTENT_TYPES,
                chosen_content_type=content_type,
                base_path=i18n_url('content:list'),
                view=request.params.get('view'))


@with_meta()
def content_detail(path, meta):
    """Update view statistics and redirect to an opener."""
    archive = open_archive()
    archive.add_view(meta.path)
    # as mixed content is possible in zipballs, it is allowed to specify which
    # content type is being viewed now explicitly, falling back to the first
    # one found in the content object
    content_type = request.params.get('content_type')
    if content_type is None:
        # pick first available content type present in content object as it was
        # not specified
        content_type = meta.content_type_names[0]

    url = i18n_url('files:path', path=meta.path)
    openers = request.app.supervisor.exts.openers
    opener_id = openers.first(content_type=content_type)
    # if there is no opener registered for this content_type, it will just
    # redirect to the file manager
    if opener_id:
        # found registered opener for content_type, so use it for displaying
        # the content item
        url += set_qparam(action='open', opener_id=opener_id).to_qs()

    if request.is_xhr:
        return str(url)

    return redirect(url)
