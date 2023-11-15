    def get_block_indentation(self, block_nb):
        """Return line indentation (character number)."""
        text = to_text_string(self.document().findBlockByNumber(block_nb).text())
        text = text.replace("\t", " "*self.tab_stop_width_spaces)
        return len(text)-len(text.lstrip())