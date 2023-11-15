    def __init__(self, *args, **kwargs):
        super(GUI, self).__init__(*args, **kwargs)

        from bleachbit import RecognizeCleanerML
        RecognizeCleanerML.RecognizeCleanerML()
        register_cleaners()

        self.set_wmclass(APP_NAME, APP_NAME)
        self.populate_window()

        # Redirect logging to the GUI.
        bb_logger = logging.getLogger('bleachbit')
        gtklog = GtkLoggerHandler(self.append_text)
        bb_logger.addHandler(gtklog)
        if 'nt' == os.name and 'windows_exe' == getattr(sys, 'frozen', None):
            # On Microsoft Windows this avoids py2exe redirecting stderr to
            # bleachbit.exe.log.
            # sys.frozen = console_exe means the console is shown
            from bleachbit import logger_sh
            bb_logger.removeHandler(logger_sh)


        Gtk.Settings.get_default().set_property('gtk-application-prefer-dark-theme', options.get('dark_mode'))

        if options.get("first_start") and 'posix' == os.name:
            pref = PreferencesDialog(self, self.cb_refresh_operations)
            pref.run()
            options.set('first_start', False)
        if bleachbit.online_update_notification_enabled and options.get("check_online_updates"):
            self.check_online_updates()
        if 'nt' == os.name:
            # BitDefender false positive.  BitDefender didn't mark BleachBit as infected or show
            # anything in its log, but sqlite would fail to import unless BitDefender was in "game mode."
            # http://bleachbit.sourceforge.net/forum/074-fails-errors
            try:
                import sqlite3
            except ImportError as e:
                self.append_text(
                    _("Error loading the SQLite module: the antivirus software may be blocking it."), 'error')

        if 'posix' == os.name and bleachbit.expanduser('~') == '/root':
            self.append_text(
                _('You are running BleachBit with administrative privileges for cleaning shared parts of the system, and references to the user profile folder will clean only the root account.'))
        if 'nt' == os.name and options.get('shred'):
            from win32com.shell.shell import IsUserAnAdmin
            if not IsUserAnAdmin():
                self.append_text(
                    _('Run BleachBit with administrator privileges to improve the accuracy of overwriting the contents of files.'))
                self.append_text('\n')