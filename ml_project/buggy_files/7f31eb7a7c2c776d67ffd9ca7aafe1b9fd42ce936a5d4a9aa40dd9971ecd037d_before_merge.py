    def index(self, locale):
        session["locale"] = locale
        refresh()
        self.update_redirect()
        return redirect(self.get_redirect())