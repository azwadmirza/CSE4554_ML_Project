    def _clear_block_deco(self):
        """Clear the folded block decorations."""
        for deco in self._block_decos:
            self.editor.decorations.remove(deco)
        self._block_decos[:] = []