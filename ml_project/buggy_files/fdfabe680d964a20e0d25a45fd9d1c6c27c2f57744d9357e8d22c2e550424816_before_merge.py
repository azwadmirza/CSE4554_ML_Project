    def __init__(self, *args, mode=None):
        QApplication.__init__(self, *args)

        try:
            # Import modules
            from classes import info
            from classes.logger import log, reroute_output

            # Log the session's start
            import time
            log.info("------------------------------------------------")
            log.info(time.asctime().center(48))
            log.info('Starting new session'.center(48))

            from classes import settings, project_data, updates, language, ui_util, logger_libopenshot
            from . import openshot_rc  # noqa
            import openshot

            # Re-route stdout and stderr to logger
            reroute_output()
        except ImportError as ex:
            tb = traceback.format_exc()
            log.error('OpenShotApp::Import Error', exc_info=1)
            QMessageBox.warning(None, "Import Error",
                                "Module: %(name)s\n\n%(tb)s" % {"name": ex.name, "tb": tb})
            # Stop launching and exit
            raise
        except Exception:
            log.error('OpenShotApp::Init Error', exc_info=1)
            sys.exit()

        # Log some basic system info
        try:
            log.info("------------------------------------------------")
            log.info(("OpenShot (version %s)" % info.SETUP['version']).center(48))
            log.info("------------------------------------------------")

            log.info("openshot-qt version: %s" % info.VERSION)
            log.info("libopenshot version: %s" % openshot.OPENSHOT_VERSION_FULL)
            log.info("platform: %s" % platform.platform())
            log.info("processor: %s" % platform.processor())
            log.info("machine: %s" % platform.machine())
            log.info("python version: %s" % platform.python_version())
            log.info("qt5 version: %s" % QT_VERSION_STR)
            log.info("pyqt5 version: %s" % PYQT_VERSION_STR)
        except Exception:
            log.debug("Error displaying dependency/system details", exc_info=1)

        # Setup application
        self.setApplicationName('openshot')
        self.setApplicationVersion(info.SETUP['version'])
        try:
            # Qt 5.7+ only
            self.setDesktopFile("org.openshot.OpenShot")
        except AttributeError:
            pass

        # Init settings
        self.settings = settings.SettingStore()
        self.settings.load()

        # Init and attach exception handler
        from classes import exceptions
        sys.excepthook = exceptions.ExceptionHandler

        # Init translation system
        language.init_language()

        # Detect minimum libopenshot version
        _ = self._tr
        libopenshot_version = openshot.OPENSHOT_VERSION_FULL
        if mode != "unittest" and libopenshot_version < info.MINIMUM_LIBOPENSHOT_VERSION:
            QMessageBox.warning(
                None, _("Wrong Version of libopenshot Detected"),
                _("<b>Version %(minimum_version)s is required</b>, but %(current_version)s was detected. Please update libopenshot or download our latest installer.") % {
                    "minimum_version": info.MINIMUM_LIBOPENSHOT_VERSION,
                    "current_version": libopenshot_version,
                    })
            # Stop launching and exit
            sys.exit()

        # Set location of OpenShot program (for libopenshot)
        openshot.Settings.Instance().PATH_OPENSHOT_INSTALL = info.PATH

        # Tests of project data loading/saving
        self.project = project_data.ProjectDataStore()

        # Init Update Manager
        self.updates = updates.UpdateManager()

        # It is important that the project is the first listener if the key gets update
        self.updates.add_listener(self.project)

        # Load ui theme if not set by OS
        ui_util.load_theme()

        # Test for permission issues (and display message if needed)
        try:
            # Create test paths
            TEST_PATH_DIR = os.path.join(info.USER_PATH, 'PERMISSION')
            TEST_PATH_FILE = os.path.join(TEST_PATH_DIR, 'test.osp')
            os.makedirs(TEST_PATH_DIR, exist_ok=True)
            with open(TEST_PATH_FILE, 'w') as f:
                f.write('{}')
                f.flush()
            # Delete test paths
            os.unlink(TEST_PATH_FILE)
            os.rmdir(TEST_PATH_DIR)
        except PermissionError as ex:
            log.error('Failed to create file %s', TEST_PATH_FILE, exc_info=1)
            QMessageBox.warning(
                None, _("Permission Error"),
                _("%(error)s. Please delete <b>%(path)s</b> and launch OpenShot again." % {
                    "error": str(ex),
                    "path": info.USER_PATH,
                }))
            # Stop launching and exit
            raise
            sys.exit()

        # Start libopenshot logging thread
        self.logger_libopenshot = logger_libopenshot.LoggerLibOpenShot()
        self.logger_libopenshot.start()

        # Track which dockable window received a context menu
        self.context_menu_object = None

        # Set Font for any theme
        if self.settings.get("theme") != "No Theme":
            # Load embedded font
            try:
                log.info("Setting font to %s" % os.path.join(info.IMAGES_PATH, "fonts", "Ubuntu-R.ttf"))
                font_id = QFontDatabase.addApplicationFont(os.path.join(info.IMAGES_PATH, "fonts", "Ubuntu-R.ttf"))
                font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
                font = QFont(font_family)
                font.setPointSizeF(10.5)
                QApplication.setFont(font)
            except Exception:
                log.debug("Error setting Ubuntu-R.ttf QFont", exc_info=1)

        # Set Experimental Dark Theme
        if self.settings.get("theme") == "Humanity: Dark":
            # Only set if dark theme selected
            log.info("Setting custom dark theme")
            self.setStyle(QStyleFactory.create("Fusion"))

            darkPalette = self.palette()

            darkPalette.setColor(QPalette.Window, QColor(53, 53, 53))
            darkPalette.setColor(QPalette.WindowText, Qt.white)
            darkPalette.setColor(QPalette.Base, QColor(25, 25, 25))
            darkPalette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            darkPalette.setColor(QPalette.Light, QColor(68, 68, 68))
            darkPalette.setColor(QPalette.Text, Qt.white)
            darkPalette.setColor(QPalette.Button, QColor(53, 53, 53))
            darkPalette.setColor(QPalette.ButtonText, Qt.white)
            darkPalette.setColor(QPalette.Highlight, QColor(42, 130, 218, 192))
            darkPalette.setColor(QPalette.HighlightedText, Qt.black)
            #
            # Disabled palette
            #
            darkPalette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(255, 255, 255, 128))
            darkPalette.setColor(QPalette.Disabled, QPalette.Base, QColor(68, 68, 68))
            darkPalette.setColor(QPalette.Disabled, QPalette.Text, QColor(255, 255, 255, 128))
            darkPalette.setColor(QPalette.Disabled, QPalette.Button, QColor(53, 53, 53, 128))
            darkPalette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(255, 255, 255, 128))
            darkPalette.setColor(QPalette.Disabled, QPalette.Highlight, QColor(151, 151, 151, 192))
            darkPalette.setColor(QPalette.Disabled, QPalette.HighlightedText, Qt.black)

            # Tooltips
            darkPalette.setColor(QPalette.ToolTipBase, QColor(42, 130, 218))
            darkPalette.setColor(QPalette.ToolTipText, Qt.white)

            self.setPalette(darkPalette)
            self.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 0px solid white; }")

        # Create main window
        from windows.main_window import MainWindow
        self.window = MainWindow(mode)

        # Reset undo/redo history
        self.updates.reset()
        self.window.updateStatusChanged(False, False)

        log.info('Process command-line arguments: %s' % args)
        if len(args[0]) == 2:
            path = args[0][1]
            if ".osp" in path:
                # Auto load project passed as argument
                self.window.OpenProjectSignal.emit(path)
            else:
                # Apply the default settings and Auto import media file
                self.project.load("")
                self.window.filesView.add_file(path)
        else:
            # Recover backup file (this can't happen until after the Main Window has completely loaded)
            self.window.RecoverBackup.emit()