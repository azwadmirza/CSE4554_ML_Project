    def setup_toolbar(self):
        """Setup toolbar"""
        load_button = create_toolbutton(
            self,
            text=_('Import data'),
            icon=ima.icon('fileimport'),
            triggered=lambda: self.import_data())

        self.save_button = create_toolbutton(
            self, text=_("Save data"),
            icon=ima.icon('filesave'),
            triggered=lambda: self.save_data(self.filename))

        self.save_button.setEnabled(False)

        save_as_button = create_toolbutton(
            self,
            text=_("Save data as..."),
            icon=ima.icon('filesaveas'),
            triggered=self.save_data)

        reset_namespace_button = create_toolbutton(
            self, text=_("Remove all variables"),
            icon=ima.icon('editdelete'),
            triggered=self.reset_namespace)

        self.search_button = create_toolbutton(
            self,
            text=_("Search variable names and types"),
            icon=ima.icon('find'),
            toggled=self.show_finder)

        self.refresh_button = create_toolbutton(
            self,
            text=_("Refresh variables"),
            icon=ima.icon('refresh'),
            triggered=lambda: self.refresh_table(interrupt=True))

        return [load_button, self.save_button, save_as_button,
                reset_namespace_button, self.search_button,
                self.refresh_button]