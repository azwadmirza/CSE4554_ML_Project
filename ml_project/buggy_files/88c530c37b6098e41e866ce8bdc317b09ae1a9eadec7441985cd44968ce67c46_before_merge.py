def _show_placeholder_for_page(context, placeholder_name, page_lookup, lang=None,
                               site=None, cache_result=True):
    """
    Shows the content of a page with a placeholder name and given lookup
    arguments in the given language.
    This is useful if you want to have some more or less static content that is
    shared among many pages, such as a footer.

    See _get_page_by_untyped_arg() for detailed information on the allowed types
    and their interpretation for the page_lookup argument.
    """
    from django.core.cache import cache
    validate_placeholder_name(placeholder_name)

    request = context.get('request', False)
    site_id = get_site_id(site)

    if not request:
        return {'content': ''}
    if lang is None:
        lang = get_language_from_request(request)

    if cache_result:
        base_key = _get_cache_key('_show_placeholder_for_page', page_lookup, lang, site_id)
        cache_key = _clean_key('%s_placeholder:%s' % (base_key, placeholder_name))
        cached_value = cache.get(cache_key)
        if cached_value:
            restore_sekizai_context(context, cached_value['sekizai'])
            return {'content': mark_safe(cached_value['content'])}
    page = _get_page_by_untyped_arg(page_lookup, request, site_id)
    if not page:
        return {'content': ''}
    try:
        placeholder = page.placeholders.get(slot=placeholder_name)
    except PlaceholderModel.DoesNotExist:
        if settings.DEBUG:
            raise
        return {'content': ''}
    watcher = Watcher(context)
    content = render_placeholder(placeholder, context, placeholder_name)
    changes = watcher.get_changes()
    if cache_result:
        cache.set(cache_key, {'content': content, 'sekizai': changes}, get_cms_setting('CACHE_DURATIONS')['content'])

    if content:
        return {'content': mark_safe(content)}
    return {'content': ''}