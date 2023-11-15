    def _applyAppTheme(self, target=None):
        self.SetArtProvider(PsychopyTabArt())
        self.GetAuiManager().SetArtProvider(PsychopyDockArt())
        for index in range(self.GetPageCount()):
            page = self.GetPage(index)
            # double buffered better rendering except if retina
            self.SetDoubleBuffered(not self.frame.isRetina)
            page._applyAppTheme()
        self.Refresh()