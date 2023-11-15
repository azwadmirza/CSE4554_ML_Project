    def styleSheet(self) -> Optional[StyleSheet]:
        model = self.model
        style_sheet = next(model.select(StyleSheet), None)
        if not style_sheet:
            style_sheet = self.model.create(StyleSheet)
            style_sheet.styleSheet = DEFAULT_STYLE_SHEET
        return style_sheet