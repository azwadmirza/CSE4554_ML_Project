        def windowWillClose_(self, notification):
            # Delete the closed instance from the dict
            i = BrowserView.get_instance('window', notification.object())
            del BrowserView.instances[i.uid]

            if BrowserView.instances == {}:
                AppHelper.callAfter(BrowserView.app.stop_, self)