    def get_plugin_actions(self):
        """Return a list of actions related to plugin"""
        self.new_project_action = create_action(self,
                                    _("New Project..."),
                                    triggered=self.create_new_project)
        self.open_project_action = create_action(self,
                                    _("Open Project..."),
                                    triggered=lambda v: self.open_project())
        self.close_project_action = create_action(self,
                                    _("Close Project"),
                                    triggered=self.close_project)
        self.delete_project_action = create_action(self,
                                    _("Delete Project"),
                                    triggered=self.delete_project)
        self.clear_recent_projects_action =\
            create_action(self, _("Clear this list"),
                          triggered=self.clear_recent_projects)
        self.edit_project_preferences_action =\
            create_action(self, _("Project Preferences"),
                          triggered=self.edit_project_preferences)
        self.recent_project_menu = QMenu(_("Recent Projects"), self)

        if self.main is not None:
            self.main.projects_menu_actions += [self.new_project_action,
                                                MENU_SEPARATOR,
                                                self.open_project_action,
                                                self.close_project_action,
                                                self.delete_project_action,
                                                MENU_SEPARATOR,
                                                self.recent_project_menu,
                                                self.toggle_view_action]

        self.setup_menu_actions()
        return []