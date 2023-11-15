def create_window(uid, title, url, width, height, resizable, fullscreen, min_size,
                  confirm_quit, background_color, debug, js_api, text_select, webview_ready):
    app = QApplication.instance() or QApplication([])

    def _create():
        browser = BrowserView(uid, title, url, width, height, resizable, fullscreen,
                              min_size, confirm_quit, background_color, debug, js_api,
                              text_select, webview_ready)
        browser.show()

    if uid == 'master':
        _create()
        app.exec_()
    else:
        i = list(BrowserView.instances.values())[0] # arbitrary instance
        i.create_window_trigger.emit(_create)