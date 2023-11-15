    def on_inspect_webview(self, inspector, webview):
        title = 'Web Inspector - {}'.format(self.window.get_title())
        uid = self.uid + '-inspector'

        inspector = BrowserView(uid, title, '', 700, 500, True, False, (300,200),
                                False, '#fff', False, None, True, self.webview_ready)
        inspector.show()
        return inspector.webview