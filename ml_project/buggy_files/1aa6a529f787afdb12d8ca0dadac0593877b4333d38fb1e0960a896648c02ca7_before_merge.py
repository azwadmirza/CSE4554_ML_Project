    def createWindow(self, webwindowtype):
        import webbrowser
        webbrowser.open(to_text_string(self.url().toString()))