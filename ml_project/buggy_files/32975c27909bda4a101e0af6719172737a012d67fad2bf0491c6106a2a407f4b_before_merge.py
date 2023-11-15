    def get_options_menu(self):
        """Return options menu"""
        reset_action = create_action(self, _("Remove all variables"),
                                     icon=ima.icon('editdelete'),
                                     triggered=self.reset_namespace)

        self.show_time_action = create_action(self, _("Show elapsed time"),
                                         toggled=self.set_elapsed_time_visible)

        env_action = create_action(
                        self,
                        _("Show environment variables"),
                        icon=ima.icon('environ'),
                        triggered=self.shellwidget.get_env
                     )

        syspath_action = create_action(
                            self,
                            _("Show sys.path contents"),
                            icon=ima.icon('syspath'),
                            triggered=self.shellwidget.get_syspath
                         )

        self.show_time_action.setChecked(self.show_elapsed_time)
        additional_actions = [reset_action,
                              MENU_SEPARATOR,
                              env_action,
                              syspath_action,
                              self.show_time_action]

        if self.menu_actions is not None:
            return self.menu_actions + additional_actions
        else:
            return additional_actions