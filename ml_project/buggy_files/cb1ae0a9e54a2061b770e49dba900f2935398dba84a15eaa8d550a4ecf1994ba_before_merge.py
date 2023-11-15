    def setup_context_menu(self):
        """Setup context menu"""
        self.undo_action = create_action(
            self, _("Undo"), icon=ima.icon('undo'),
            shortcut=get_shortcut('editor', 'undo'), triggered=self.undo)
        self.redo_action = create_action(
            self, _("Redo"), icon=ima.icon('redo'),
            shortcut=get_shortcut('editor', 'redo'), triggered=self.redo)
        self.cut_action = create_action(
            self, _("Cut"), icon=ima.icon('editcut'),
            shortcut=get_shortcut('editor', 'cut'), triggered=self.cut)
        self.copy_action = create_action(
            self, _("Copy"), icon=ima.icon('editcopy'),
            shortcut=get_shortcut('editor', 'copy'), triggered=self.copy)
        self.paste_action = create_action(
            self, _("Paste"), icon=ima.icon('editpaste'),
            shortcut=get_shortcut('editor', 'paste'), triggered=self.paste)
        selectall_action = create_action(
            self, _("Select All"), icon=ima.icon('selectall'),
            shortcut=get_shortcut('editor', 'select all'),
            triggered=self.selectAll)
        toggle_comment_action = create_action(
            self, _("Comment")+"/"+_("Uncomment"), icon=ima.icon('comment'),
            shortcut=get_shortcut('editor', 'toggle comment'),
            triggered=self.toggle_comment)
        self.clear_all_output_action = create_action(
            self, _("Clear all ouput"), icon=ima.icon('ipython_console'),
            triggered=self.clear_all_output)
        self.ipynb_convert_action = create_action(
            self, _("Convert to Python script"), icon=ima.icon('python'),
            triggered=self.convert_notebook)
        self.gotodef_action = create_action(
            self, _("Go to definition"),
            shortcut=get_shortcut('editor', 'go to definition'),
            triggered=self.go_to_definition_from_cursor)

        # Run actions
        self.run_cell_action = create_action(
            self, _("Run cell"), icon=ima.icon('run_cell'),
            shortcut=get_shortcut('editor', 'run cell'),
            triggered=self.sig_run_cell.emit)
        self.run_cell_and_advance_action = create_action(
            self, _("Run cell and advance"), icon=ima.icon('run_cell'),
            shortcut=get_shortcut('editor', 'run cell and advance'),
            triggered=self.sig_run_cell_and_advance.emit)
        self.re_run_last_cell_action = create_action(
            self, _("Re-run last cell"), icon=ima.icon('run_cell'),
            shortcut=get_shortcut('editor', 're-run last cell'),
            triggered=self.sig_re_run_last_cell.emit)
        self.run_selection_action = create_action(
            self, _("Run &selection or current line"),
            icon=ima.icon('run_selection'),
            shortcut=get_shortcut('editor', 'run selection'),
            triggered=self.sig_run_selection.emit)

        # Zoom actions
        zoom_in_action = create_action(
            self, _("Zoom in"), icon=ima.icon('zoom_in'),
            shortcut=QKeySequence(QKeySequence.ZoomIn),
            triggered=self.zoom_in.emit)
        zoom_out_action = create_action(
            self, _("Zoom out"), icon=ima.icon('zoom_out'),
            shortcut=QKeySequence(QKeySequence.ZoomOut),
            triggered=self.zoom_out.emit)
        zoom_reset_action = create_action(
            self, _("Zoom reset"), shortcut=QKeySequence("Ctrl+0"),
            triggered=self.zoom_reset.emit)

        # Docstring
        writer = self.writer_docstring
        self.docstring_action = create_action(
            self, _("Generate docstring"),
            shortcut=get_shortcut('editor', 'docstring'),
            triggered=writer.write_docstring_at_first_line_of_function)

        # Build menu
        self.menu = QMenu(self)
        actions_1 = [self.run_cell_action, self.run_cell_and_advance_action,
                     self.re_run_last_cell_action, self.run_selection_action,
                     self.gotodef_action, None, self.undo_action,
                     self.redo_action, None, self.cut_action,
                     self.copy_action, self.paste_action, selectall_action]
        actions_2 = [None, zoom_in_action, zoom_out_action, zoom_reset_action,
                     None, toggle_comment_action, self.docstring_action]
        if nbformat is not None:
            nb_actions = [self.clear_all_output_action,
                          self.ipynb_convert_action, None]
            actions = actions_1 + nb_actions + actions_2
            add_actions(self.menu, actions)
        else:
            actions = actions_1 + actions_2
            add_actions(self.menu, actions)

        # Read-only context-menu
        self.readonly_menu = QMenu(self)
        add_actions(self.readonly_menu,
                    (self.copy_action, None, selectall_action,
                     self.gotodef_action))