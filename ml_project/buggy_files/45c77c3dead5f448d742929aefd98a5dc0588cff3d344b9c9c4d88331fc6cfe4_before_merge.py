    def _applyAppTheme(self, target=None):
        self.SetArtProvider(PsychopyTabArt())
        self.GetAuiManager().SetArtProvider(PsychopyDockArt())
        for index in range(self.GetPageCount()):
            page = self.GetPage(index)
            # double buffered better rendering except if retina
            self.SetDoubleBuffered(self.frame.IsDoubleBuffered())
            page._applyAppTheme()
        self.Refresh()