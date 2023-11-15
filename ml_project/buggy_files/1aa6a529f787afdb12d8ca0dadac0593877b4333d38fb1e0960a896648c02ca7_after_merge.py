    def createWindow(self, webwindowtype):
        import webbrowser
        # See: spyder-ide/spyder#9849
        try:
            webbrowser.open(to_text_string(self.url().toString()))
        except ValueError:
            pass