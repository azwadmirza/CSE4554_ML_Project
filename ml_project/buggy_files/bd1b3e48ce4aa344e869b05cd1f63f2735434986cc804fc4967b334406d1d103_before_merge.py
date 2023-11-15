    def build_app_menu(self):
        builder = Gtk.Builder()
        builder.add_from_file(os.path.join(bleachbit.bleachbit_exe_path, 'data', 'app-menu.ui'))
        menu = builder.get_object('app-menu')
        self.set_app_menu(menu)

        # set up mappings between <attribute name="action"> in app-menu.ui and methods in this class
        actions = {'shredFiles': self.cb_shred_file,
                   'shredFolders': self.cb_shred_folder,
                   'wipeFreeSpace': self.cb_wipe_free_space,
                   'shredQuit': self.cb_shred_quit,
                   'preferences': self.cb_preferences_dialog,
                   'diagnostics': self.diagnostic_dialog,
                   'about': self.about,
                   'quit': self.quit}

        for actionName, callback in actions.items():
            action = Gio.SimpleAction.new(actionName, None)
            action.connect('activate', callback)
            self.add_action(action)

        # help needs more parameters and needs to be declared separately
        helpAction = Gio.SimpleAction.new('help', None)
        helpAction.connect('activate', GuiBasic.open_url, bleachbit.help_contents_url, self._window)
        self.add_action(helpAction)