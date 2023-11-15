    def set_font(self, font, fixed_font=None):
        settings = self.page().settings()
        for fontfamily in (settings.StandardFont, settings.SerifFont,
                           settings.SansSerifFont, settings.CursiveFont,
                           settings.FantasyFont):
            settings.setFontFamily(fontfamily, font.family())
        if fixed_font is not None:
            settings.setFontFamily(settings.FixedFont, fixed_font.family())
        size = font.pointSize()
        settings.setFontSize(settings.DefaultFontSize, size)
        settings.setFontSize(settings.DefaultFixedFontSize, size)