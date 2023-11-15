    def __init__(self, uac=True, shred_paths=None, exit=False):
        if uac and 'nt' == os.name and Windows.elevate_privileges():
            # privileges escalated in other process
            sys.exit(0)
        Gtk.Application.__init__(self, application_id='org.gnome.Bleachbit', flags=Gio.ApplicationFlags.FLAGS_NONE)
        if not exit:
            from bleachbit import RecognizeCleanerML
            RecognizeCleanerML.RecognizeCleanerML()
            register_cleaners()
        GObject.threads_init()

        if shred_paths:
            self._shred_paths = shred_paths
            return
        if 'nt' == os.name:
            # BitDefender false positive.  BitDefender didn't mark BleachBit as infected or show
            # anything in its log, but sqlite would fail to import unless BitDefender was in "game mode."
            # https://www.bleachbit.org/forum/074-fails-errors
            try:
                import sqlite3
            except ImportError:
                logger.exception(_("Error loading the SQLite module: the antivirus software may be blocking it."))
        if exit:
            # This is used for automated testing of whether the GUI can start.
            print('Success')
            GObject.idle_add(lambda: self.quit(), priority=GObject.PRIORITY_LOW)