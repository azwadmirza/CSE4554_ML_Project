    def register_editorstack(self, editorstack):
        self.editorstacks.append(editorstack)
        logger.debug("EditorWidget.register_editorstack: %r" % editorstack)
        self.__print_editorstacks()
        self.plugin.last_focus_editorstack[self.parent()] = editorstack
        editorstack.set_closable( len(self.editorstacks) > 1 )
        editorstack.set_outlineexplorer(self.outlineexplorer)
        editorstack.set_find_widget(self.find_widget)
        editorstack.reset_statusbar.connect(self.readwrite_status.hide)
        editorstack.reset_statusbar.connect(self.encoding_status.hide)
        editorstack.reset_statusbar.connect(self.cursorpos_status.hide)
        editorstack.readonly_changed.connect(
                                        self.readwrite_status.update_readonly)
        editorstack.encoding_changed.connect(
                                         self.encoding_status.update_encoding)
        editorstack.sig_editor_cursor_position_changed.connect(
                     self.cursorpos_status.update_cursor_position)
        editorstack.sig_refresh_eol_chars.connect(self.eol_status.update_eol)
        self.plugin.register_editorstack(editorstack)
        oe_btn = create_toolbutton(self)
        oe_btn.setDefaultAction(self.outlineexplorer.visibility_action)
        editorstack.add_corner_widgets_to_tabbar([5, oe_btn])