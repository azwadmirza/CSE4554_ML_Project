    def _clear_block_deco(self):
        """Clear the folded block decorations."""
        for deco_line in self._block_decos:
            deco = self._block_decos[deco_line]
            self.editor.decorations.remove(deco)
        self._block_decos = {}