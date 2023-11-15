        def show_inspector(self):
            uid = self.parent().uid + '-inspector'
            try:
                # If inspector already exists, bring it to the front
                BrowserView.instances[uid].raise_()
                BrowserView.instances[uid].activateWindow()
            except KeyError:
                title = 'Web Inspector - {}'.format(self.parent().title)
                url = 'http://localhost:{}'.format(BrowserView.inspector_port)

                inspector = BrowserView(uid, title, url, 700, 500, True, False, (300, 200),
                                        False, '#fff', False, None, True, self.parent().webview_ready)
                inspector.show()