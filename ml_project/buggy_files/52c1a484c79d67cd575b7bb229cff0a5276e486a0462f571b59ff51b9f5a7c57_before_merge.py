    def enter(self, itemClicked=None):
        row = self.current_row()
        stack_index = self.paths.index(self.filtered_path[row])
        self.plugin = self.widgets[stack_index][1]
        plugin_index = self.plugins_instances.index(self.plugin)
        # Count the real index in the tabWidget of the
        # current plugin
        real_index = self.get_stack_index(stack_index,
                                          plugin_index)
        self.sig_goto_file.emit(real_index,
                                self.plugin.get_current_tab_manager())
        self.accept()