    def _add_fold_decoration(self, block, end_line):
        """
        Add fold decorations (boxes arround a folded block in the editor
        widget).
        """
        start_line = block.blockNumber()
        text = self.editor.get_text_region(start_line + 1, end_line)
        draw_order = DRAW_ORDERS.get('codefolding')
        deco = TextDecoration(block, draw_order=draw_order)
        deco.signals.clicked.connect(self._on_fold_deco_clicked)
        deco.tooltip = text
        deco.block = block
        deco.select_line()
        deco.set_outline(drift_color(
            self._get_scope_highlight_color(), 110))
        deco.set_background(self._get_scope_highlight_color())
        deco.set_foreground(QColor('#808080'))
        self._block_decos.append(deco)
        self.editor.decorations.add(deco)