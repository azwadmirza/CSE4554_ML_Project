def _get_tab_registry(win_id, tab_id):
    """Get the registry of a tab."""
    if tab_id is None:
        raise ValueError("Got tab_id None (win_id {})".format(win_id))
    if tab_id == 'current' and win_id is None:
        app = get('app')
        window = app.activeWindow()
        if window is None or not hasattr(window, 'win_id'):
            raise RegistryUnavailableError('tab')
        win_id = window.win_id
    elif win_id is not None:
        window = window_registry[win_id]
    else:
        raise TypeError("window is None with scope tab!")

    if tab_id == 'current':
        tabbed_browser = get('tabbed-browser', scope='window', window=win_id)
        tab = tabbed_browser.widget.currentWidget()
        if tab is None:
            raise RegistryUnavailableError('window')
        tab_id = tab.tab_id
    tab_registry = get('tab-registry', scope='window', window=win_id)
    try:
        return tab_registry[tab_id].registry
    except AttributeError:
        raise RegistryUnavailableError('tab')