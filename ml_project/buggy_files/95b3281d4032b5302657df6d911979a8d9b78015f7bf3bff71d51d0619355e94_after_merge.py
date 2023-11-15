    def refresh_decorations(self, force=False):
        """
        Refresh decorations colors. This function is called by the syntax
        highlighter when the style changed so that we may update our
        decorations colors according to the new style.
        """
        cursor = self.editor.textCursor()
        if (self._prev_cursor is None or force or
                self._prev_cursor.blockNumber() != cursor.blockNumber()):
            for deco_line in self._block_decos:
                deco = self._block_decos[deco_line]
                self.editor.decorations.remove(deco)
            for deco_line in self._block_decos:
                deco = self._block_decos[deco_line]
                deco.set_outline(drift_color(
                    self._get_scope_highlight_color(), 110))
                deco.set_background(self._get_scope_highlight_color())
                self.editor.decorations.add(deco)
        self._prev_cursor = cursor