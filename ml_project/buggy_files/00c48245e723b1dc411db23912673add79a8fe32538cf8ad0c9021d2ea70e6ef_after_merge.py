def debug_cache_stats():
    """Print LRU cache stats."""
    prefix_info = configdata.is_valid_prefix.cache_info()
    # pylint: disable=protected-access
    render_stylesheet_info = config._render_stylesheet.cache_info()
    # pylint: enable=protected-access

    history_info = None
    try:
        from PyQt5.QtWebKit import QWebHistoryInterface
        interface = QWebHistoryInterface.defaultInterface()
        if interface is not None:
            history_info = interface.historyContains.cache_info()
    except ImportError:
        pass

    tabbed_browser = objreg.get('tabbed-browser', scope='window',
                                window='last-focused')
    # pylint: disable=protected-access
    tab_bar = tabbed_browser.widget.tabBar()
    tabbed_browser_info = tab_bar._minimum_tab_size_hint_helper.cache_info()
    # pylint: enable=protected-access

    log.misc.debug('is_valid_prefix: {}'.format(prefix_info))
    log.misc.debug('_render_stylesheet: {}'.format(render_stylesheet_info))
    log.misc.debug('history: {}'.format(history_info))
    log.misc.debug('tab width cache: {}'.format(tabbed_browser_info))