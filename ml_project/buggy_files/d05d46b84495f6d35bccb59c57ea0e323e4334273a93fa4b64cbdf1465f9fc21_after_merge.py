def _buffer(skip_win_id=None):
    """Helper to get the completion model for buffer/other_buffer.

    Args:
        skip_win_id: The id of the window to skip, or None to include all.
    """
    def delete_buffer(data):
        """Close the selected tab."""
        win_id, tab_index = data[0].split('/')
        tabbed_browser = objreg.get('tabbed-browser', scope='window',
                                    window=int(win_id))
        tabbed_browser.on_tab_close_requested(int(tab_index) - 1)

    model = completionmodel.CompletionModel(column_widths=(6, 40, 54))

    for win_id in objreg.window_registry:
        if skip_win_id is not None and win_id == skip_win_id:
            continue
        tabbed_browser = objreg.get('tabbed-browser', scope='window',
                                    window=win_id)
        if tabbed_browser.shutting_down:
            continue
        tabs = []
        for idx in range(tabbed_browser.widget.count()):
            tab = tabbed_browser.widget.widget(idx)
            tabs.append(("{}/{}".format(win_id, idx + 1),
                         tab.url().toDisplayString(),
                         tabbed_browser.widget.page_title(idx)))
        cat = listcategory.ListCategory("{}".format(win_id), tabs,
                                        delete_func=delete_buffer)
        model.add_category(cat)

    return model