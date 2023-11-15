    def get_plugin_actions(self):
        """Return a list of actions related to plugin"""
        quit_action = create_action(self, _("&Quit"),
                                    icon=ima.icon('exit'), 
                                    tip=_("Quit"),
                                    triggered=self.quit)
        self.register_shortcut(quit_action, "_", "Quit", "Ctrl+Q")
        run_action = create_action(self, _("&Run..."), None,
                            ima.icon('run_small'),
                            _("Run a Python script"),
                            triggered=self.run_script)
        environ_action = create_action(self,
                            _("Environment variables..."),
                            icon=ima.icon('environ'),
                            tip=_("Show and edit environment variables"
                                        " (for current session)"),
                            triggered=self.show_env)
        syspath_action = create_action(self,
                            _("Show sys.path contents..."),
                            icon=ima.icon('syspath'),
                            tip=_("Show (read-only) sys.path"),
                            triggered=self.show_syspath)
        buffer_action = create_action(self,
                            _("Buffer..."), None,
                            tip=_("Set maximum line count"),
                            triggered=self.change_max_line_count)
        exteditor_action = create_action(self,
                            _("External editor path..."), None, None,
                            _("Set external editor executable path"),
                            triggered=self.change_exteditor)
        wrap_action = create_action(self,
                            _("Wrap lines"),
                            toggled=self.toggle_wrap_mode)
        wrap_action.setChecked(self.get_option('wrap'))
        codecompletion_action = create_action(self,
                                          _("Automatic code completion"),
                                          toggled=self.toggle_codecompletion)
        codecompletion_action.setChecked(self.get_option('codecompletion/auto'))
        
        option_menu = QMenu(_('Internal console settings'), self)
        option_menu.setIcon(ima.icon('tooloptions'))
        add_actions(option_menu, (buffer_action, wrap_action,
                                  codecompletion_action,
                                  exteditor_action))
                    
        plugin_actions = [None, run_action, environ_action, syspath_action,
                          option_menu, MENU_SEPARATOR, quit_action,
                          self.undock_action]

        return plugin_actions