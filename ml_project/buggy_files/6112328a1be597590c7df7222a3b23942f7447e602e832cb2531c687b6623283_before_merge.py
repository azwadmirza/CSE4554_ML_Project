    def style(self, node: StyleNode) -> Style:
        style_sheet = self.styleSheet
        return {
            **FALLBACK_STYLE,  # type: ignore[misc]
            **style_sheet.match(node),
        }