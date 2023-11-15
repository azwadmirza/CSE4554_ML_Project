    def create_shortcuts(self):
        """Create local shortcuts"""
        # --- Configurable shortcuts
        inspect = config_shortcut(self.inspect_current_object, context='Editor',
                                  name='Inspect current object', parent=self)
        # TODO: Cleaner way to do this?
        app = QCoreApplication.instance()
        set_breakpoint = config_shortcut(self.set_or_clear_breakpoint,
                                         context='Editor', name='Breakpoint',
                                         parent=self)
        set_cond_breakpoint = config_shortcut(
                                    self.set_or_edit_conditional_breakpoint,
                                    context='Editor',
                                    name='Conditional breakpoint',
                                    parent=self)
        gotoline = config_shortcut(self.go_to_line, context='Editor',
                                   name='Go to line', parent=self)
        tab = config_shortcut(lambda: self.tab_navigation_mru(forward=False),
                              context='Editor',
                              name='Go to previous file', parent=self)
        tabshift = config_shortcut(self.tab_navigation_mru, context='Editor',
                                   name='Go to next file', parent=self)
        prevtab = config_shortcut(lambda: self.tabs.tab_navigate(-1),
                                  context='Editor',
                                  name='Cycle to previous file', parent=self)
        nexttab = config_shortcut(lambda: self.tabs.tab_navigate(1),
                                  context='Editor',
                                  name='Cycle to next file', parent=self)
        run_selection = config_shortcut(self.run_selection, context='Editor',
                                        name='Run selection', parent=self)
        new_file = config_shortcut(lambda : self.sig_new_file[()].emit(),
                                   context='Editor', name='New file',
                                   parent=self)
        open_file = config_shortcut(lambda : self.plugin_load[()].emit(),
                                    context='Editor', name='Open file',
                                    parent=self)
        save_file = config_shortcut(self.save, context='Editor',
                                    name='Save file', parent=self)
        save_all = config_shortcut(self.save_all, context='Editor',
                                   name='Save all', parent=self)
        save_as = config_shortcut(lambda : self.sig_save_as.emit(),
                                  context='Editor', name='Save As',
                                  parent=self)
        close_all = config_shortcut(self.close_all_files, context='Editor',
                                    name='Close all', parent=self)
        prev_edit_pos = config_shortcut(lambda : self.sig_prev_edit_pos.emit(),
                                        context="Editor",
                                        name="Last edit location",
                                        parent=self)
        prev_cursor = config_shortcut(lambda : self.sig_prev_cursor.emit(),
                                      context="Editor",
                                      name="Previous cursor position",
                                      parent=self)
        next_cursor = config_shortcut(lambda : self.sig_next_cursor.emit(),
                                      context="Editor",
                                      name="Next cursor position",
                                      parent=self)
        zoom_in_1 = config_shortcut(lambda : self.zoom_in.emit(),
                                      context="Editor",
                                      name="zoom in 1",
                                      parent=self)
        zoom_in_2 = config_shortcut(lambda : self.zoom_in.emit(),
                                      context="Editor",
                                      name="zoom in 2",
                                      parent=self)
        zoom_out = config_shortcut(lambda : self.zoom_out.emit(),
                                      context="Editor",
                                      name="zoom out",
                                      parent=self)
        zoom_reset = config_shortcut(lambda: self.zoom_reset.emit(),
                                      context="Editor",
                                      name="zoom reset",
                                      parent=self)
        close_file_1 = config_shortcut(self.close_file,
                                      context="Editor",
                                      name="close file 1",
                                      parent=self)
        close_file_2 = config_shortcut(self.close_file,
                                      context="Editor",
                                      name="close file 2",
                                      parent=self)
        run_cell = config_shortcut(self.run_cell,
                                      context="Editor",
                                      name="run cell",
                                      parent=self)
        debug_cell = config_shortcut(self.debug_cell,
                                     context="Editor",
                                     name="debug cell",
                                     parent=self)
        run_cell_and_advance = config_shortcut(self.run_cell_and_advance,
                                      context="Editor",
                                      name="run cell and advance",
                                      parent=self)
        go_to_next_cell = config_shortcut(self.advance_cell,
                                          context="Editor",
                                          name="go to next cell",
                                          parent=self)
        go_to_previous_cell = config_shortcut(lambda: self.advance_cell(reverse=True),
                                              context="Editor",
                                              name="go to previous cell",
                                              parent=self)
        re_run_last_cell = config_shortcut(self.re_run_last_cell,
                                      context="Editor",
                                      name="re-run last cell",
                                      parent=self)
        prev_warning = config_shortcut(lambda: self.sig_prev_warning.emit(),
                                       context="Editor",
                                       name="Previous warning",
                                       parent=self)
        next_warning = config_shortcut(lambda: self.sig_next_warning.emit(),
                                       context="Editor",
                                       name="Next warning",
                                       parent=self)
        split_vertically = config_shortcut(lambda: self.sig_split_vertically.emit(),
                                           context="Editor",
                                           name="split vertically",
                                           parent=self)
        split_horizontally = config_shortcut(lambda: self.sig_split_horizontally.emit(),
                                             context="Editor",
                                             name="split horizontally",
                                             parent=self)
        close_split = config_shortcut(self.close_split,
                                      context="Editor",
                                      name="close split panel",
                                      parent=self)

        # Return configurable ones
        return [inspect, set_breakpoint, set_cond_breakpoint, gotoline, tab,
                tabshift, run_selection, new_file, open_file, save_file,
                save_all, save_as, close_all, prev_edit_pos, prev_cursor,
                next_cursor, zoom_in_1, zoom_in_2, zoom_out, zoom_reset,
                close_file_1, close_file_2, run_cell, debug_cell,
                run_cell_and_advance,
                go_to_next_cell, go_to_previous_cell, re_run_last_cell,
                prev_warning, next_warning, split_vertically,
                split_horizontally, close_split,
                prevtab, nexttab]