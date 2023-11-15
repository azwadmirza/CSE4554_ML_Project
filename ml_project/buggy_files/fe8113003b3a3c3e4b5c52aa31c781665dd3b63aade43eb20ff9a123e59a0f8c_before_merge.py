    def _refresh_outlineexplorer(self, index=None, update=True, clear=False):
        """Refresh outline explorer panel"""
        oe = self.outlineexplorer
        if oe is None:
            return
        if index is None:
            index = self.get_stack_index()
        if self.data:
            finfo = self.data[index]
            oe.setEnabled(True)
            if finfo.editor.oe_proxy is None:
                finfo.editor.oe_proxy = OutlineExplorerProxyEditor(
                    finfo.editor, finfo.filename)
            oe.set_current_editor(finfo.editor.oe_proxy,
                                  update=update, clear=clear)
            if index != self.get_stack_index():
                # The last file added to the outline explorer is not the
                # currently focused one in the editor stack. Therefore,
                # we need to force a refresh of the outline explorer to set
                # the current editor to the currently focused one in the
                # editor stack. See spyder-ide/spyder#8015.
                self._refresh_outlineexplorer(update=False)
                return
        self._sync_outlineexplorer_file_order()