    def __init__(self, auto_exit, *args, **kwargs):
        super(GUI, self).__init__(*args, **kwargs)

        self.auto_exit = auto_exit

        self.set_wmclass(APP_NAME, APP_NAME)
        self.populate_window()

        # Redirect logging to the GUI.
        bb_logger = logging.getLogger('bleachbit')
        from bleachbit.Log import GtkLoggerHandler
        self.gtklog = GtkLoggerHandler(self.append_text)
        bb_logger.addHandler(self.gtklog)

        # process any delayed logs
        from bleachbit.Log import DelayLog
        if isinstance(sys.stderr, DelayLog):
            for msg in sys.stderr.read():
                self.append_text(msg)
            # if stderr was redirected - keep redirecting it
            sys.stderr = self.gtklog

        Gtk.Settings.get_default().set_property(
            'gtk-application-prefer-dark-theme', options.get('dark_mode'))

        if options.is_corrupt():
            logger.error(
                _('Resetting the configuration file because it is corrupt: %s') % bleachbit.options_file)
            bleachbit.Options.init_configuration()

        if options.get("first_start") and not auto_exit:
            if os.name == 'posix':
                self.append_text(
                    _('Access the application menu by clicking the hamburger icon on the title bar.'))
                pref = PreferencesDialog(self, self.cb_refresh_operations)
                pref.run()
            if os.name == 'nt':
                self.append_text(
                    _('Access the application menu by clicking the logo on the title bar.'))
            options.set('first_start', False)
        if os.name == 'nt':
            # BitDefender false positive.  BitDefender didn't mark BleachBit as infected or show
            # anything in its log, but sqlite would fail to import unless BitDefender was in "game mode."
            # http://bleachbit.sourceforge.net/forum/074-fails-errors
            try:
                import sqlite3
            except ImportError as e:
                self.append_text(
                    _("Error loading the SQLite module: the antivirus software may be blocking it."), 'error')

        if os.name == 'posix' and bleachbit.expanduser('~') == '/root':
            self.append_text(
                _('You are running BleachBit with administrative privileges for cleaning shared parts of the system, and references to the user profile folder will clean only the root account.'))
        if os.name == 'nt' and options.get('shred'):
            from win32com.shell.shell import IsUserAnAdmin
            if not IsUserAnAdmin():
                self.append_text(
                    _('Run BleachBit with administrator privileges to improve the accuracy of overwriting the contents of files.'))
                self.append_text('\n')

        GLib.idle_add(self.cb_refresh_operations)