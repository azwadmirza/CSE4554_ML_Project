    def fontMGR(self, mgr):
        if isinstance(mgr, FontManager):
            allFonts = mgr
        else:
            raise TypeError(f"Could not set font manager for TextBox2 object `{self.name}`, must be supplied with a FontManager object")