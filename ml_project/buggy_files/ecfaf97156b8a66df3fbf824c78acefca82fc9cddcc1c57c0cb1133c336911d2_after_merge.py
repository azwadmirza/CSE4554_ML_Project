    def updateStartOnLogon(self):
        """
        Configure Bitmessage to start on startup (or remove the
        configuration) based on the setting in the keys.dat file
        """
        startonlogon = BMConfigParser().safeGetBoolean(
            'bitmessagesettings', 'startonlogon')
        if sys.platform.startswith('win'):  # Auto-startup for Windows
            RUN_PATH = "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"
            settings = QtCore.QSettings(
                RUN_PATH, QtCore.QSettings.NativeFormat)
            # In case the user moves the program and the registry entry is
            # no longer valid, this will delete the old registry entry.
            if startonlogon:
                settings.setValue("PyBitmessage", sys.argv[0])
            else:
                settings.remove("PyBitmessage")
        else:
            try:  # get desktop plugin if any
                self.desktop = get_plugin('desktop')()
                self.desktop.adjust_startonlogon(startonlogon)
            except (NameError, TypeError):
                self.desktop = False