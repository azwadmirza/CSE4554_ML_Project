    def __init__(self, options=None):
        QMainWindow.__init__(self)

        qapp = QApplication.instance()
        if PYQT5:
            # Enabling scaling for high dpi
            qapp.setAttribute(Qt.AA_UseHighDpiPixmaps)
        self.default_style = str(qapp.style().objectName())

        self.dialog_manager = DialogManager()

        self.init_workdir = options.working_directory
        self.profile = options.profile
        self.multithreaded = options.multithreaded
        self.new_instance = options.new_instance
        self.open_project = options.open_project

        self.debug_print("Start of MainWindow constructor")
        
        self.setFocusPolicy(Qt.StrongFocus)

        def signal_handler(signum, frame=None):
            """Handler for signals."""
            sys.stdout.write('Handling signal: %s\n' % signum)
            sys.stdout.flush()
            QApplication.quit()

        if os.name == "nt":
            try:
                import win32api
                win32api.SetConsoleCtrlHandler(signal_handler, True)
            except ImportError:
                pass
        else:
            signal.signal(signal.SIGTERM, signal_handler)

        # Use a custom Qt stylesheet
        if sys.platform == 'darwin':
            spy_path = get_module_source_path('spyder')
            img_path = osp.join(spy_path, 'images')
            mac_style = open(osp.join(spy_path, 'app', 'mac_stylesheet.qss')).read()
            mac_style = mac_style.replace('$IMAGE_PATH', img_path)
            self.setStyleSheet(mac_style)

        # Create our TEMPDIR
        if not osp.isdir(programs.TEMPDIR):
            os.mkdir(programs.TEMPDIR)

        # Shortcut management data
        self.shortcut_data = []

        # Loading Spyder path
        self.path = []
        self.project_path = []
        if osp.isfile(self.SPYDER_PATH):
            self.path, _x = encoding.readlines(self.SPYDER_PATH)
            self.path = [name for name in self.path if osp.isdir(name)]
        self.remove_path_from_sys_path()
        self.add_path_to_sys_path()

        # Plugins
        self.console = None
        self.workingdirectory = None
        self.editor = None
        self.explorer = None
        self.help = None
        self.onlinehelp = None
        self.projects = None
        self.outlineexplorer = None
        self.historylog = None
        self.extconsole = None
        self.ipyconsole = None
        self.variableexplorer = None
        self.findinfiles = None
        self.thirdparty_plugins = []

        # Tour  # TODO: Should I consider it a plugin?? or?
        self.tour = None
        self.tours_available = None

        # Check for updates Thread and Worker, refereces needed to prevent
        # segfaulting
        self.check_updates_action = None
        self.thread_updates = None
        self.worker_updates = None
        self.give_updates_feedback = True

        # Preferences
        from spyder.plugins.configdialog import (MainConfigPage, 
                                                 ColorSchemeConfigPage)
        from spyder.plugins.shortcuts import ShortcutsConfigPage
        from spyder.plugins.runconfig import RunConfigPage
        from spyder.plugins.maininterpreter import MainInterpreterConfigPage
        self.general_prefs = [MainConfigPage, ShortcutsConfigPage,
                              ColorSchemeConfigPage, MainInterpreterConfigPage,
                              RunConfigPage]
        self.prefs_index = None
        self.prefs_dialog_size = None

        # Quick Layouts and Dialogs
        from spyder.plugins.layoutdialog import (LayoutSaveDialog,
                                                 LayoutSettingsDialog)
        self.dialog_layout_save = LayoutSaveDialog
        self.dialog_layout_settings = LayoutSettingsDialog

        # Actions
        self.lock_dockwidgets_action = None
        self.show_toolbars_action = None
        self.close_dockwidget_action = None
        self.undo_action = None
        self.redo_action = None
        self.copy_action = None
        self.cut_action = None
        self.paste_action = None
        self.selectall_action = None
        self.maximize_action = None
        self.fullscreen_action = None

        # Menu bars
        self.file_menu = None
        self.file_menu_actions = []
        self.edit_menu = None
        self.edit_menu_actions = []
        self.search_menu = None
        self.search_menu_actions = []
        self.source_menu = None
        self.source_menu_actions = []
        self.run_menu = None
        self.run_menu_actions = []
        self.debug_menu = None
        self.debug_menu_actions = []
        self.consoles_menu = None
        self.consoles_menu_actions = []
        self.projects_menu = None
        self.projects_menu_actions = []
        self.tools_menu = None
        self.tools_menu_actions = []
        self.external_tools_menu = None # We must keep a reference to this,
        # otherwise the external tools menu is lost after leaving setup method
        self.external_tools_menu_actions = []
        self.view_menu = None
        self.plugins_menu = None
        self.plugins_menu_actions = []
        self.toolbars_menu = None
        self.help_menu = None
        self.help_menu_actions = []

        # Status bar widgets
        self.mem_status = None
        self.cpu_status = None

        # Toolbars
        self.visible_toolbars = []
        self.toolbarslist = []
        self.main_toolbar = None
        self.main_toolbar_actions = []
        self.file_toolbar = None
        self.file_toolbar_actions = []
        self.edit_toolbar = None
        self.edit_toolbar_actions = []
        self.search_toolbar = None
        self.search_toolbar_actions = []
        self.source_toolbar = None
        self.source_toolbar_actions = []
        self.run_toolbar = None
        self.run_toolbar_actions = []
        self.debug_toolbar = None
        self.debug_toolbar_actions = []
        self.layout_toolbar = None
        self.layout_toolbar_actions = []


        # Set Window title and icon
        if DEV is not None:
            title = "Spyder %s (Python %s.%s)" % (__version__,
                                                  sys.version_info[0],
                                                  sys.version_info[1])
        else:
            title = "Spyder (Python %s.%s)" % (sys.version_info[0],
                                               sys.version_info[1])
        if DEBUG:
            title += " [DEBUG MODE %d]" % DEBUG
        if options.window_title is not None:
            title += ' -- ' + options.window_title

        self.base_title = title
        self.update_window_title()
        resample = os.name != 'nt'
        icon = ima.icon('spyder', resample=resample)
        # Resampling SVG icon only on non-Windows platforms (see Issue 1314):
        self.setWindowIcon(icon)
        if set_windows_appusermodelid != None:
            res = set_windows_appusermodelid()
            debug_print("appusermodelid: " + str(res))

        # Setting QTimer if running in travis
        test_travis = os.environ.get('TEST_CI_APP', None)
        if test_travis is not None:
            global MAIN_APP
            timer_shutdown_time = 30000
            self.timer_shutdown = QTimer(self)
            self.timer_shutdown.timeout.connect(MAIN_APP.quit)
            self.timer_shutdown.start(timer_shutdown_time)

        # Showing splash screen
        self.splash = SPLASH
        if CONF.get('main', 'current_version', '') != __version__:
            CONF.set('main', 'current_version', __version__)
            # Execute here the actions to be performed only once after
            # each update (there is nothing there for now, but it could
            # be useful some day...)

        # List of satellite widgets (registered in add_dockwidget):
        self.widgetlist = []

        # Flags used if closing() is called by the exit() shell command
        self.already_closed = False
        self.is_starting_up = True
        self.is_setting_up = True

        self.dockwidgets_locked = CONF.get('main', 'panes_locked')
        self.floating_dockwidgets = []
        self.window_size = None
        self.window_position = None
        self.state_before_maximizing = None
        self.current_quick_layout = None
        self.previous_layout_settings = None  # TODO: related to quick layouts
        self.last_plugin = None
        self.fullscreen_flag = None # isFullscreen does not work as expected
        # The following flag remember the maximized state even when
        # the window is in fullscreen mode:
        self.maximized_flag = None

        # Track which console plugin type had last focus
        # True: Console plugin
        # False: IPython console plugin
        self.last_console_plugin_focus_was_python = True

        # To keep track of the last focused widget
        self.last_focused_widget = None
        self.previous_focused_widget = None

        # Server to open external files on a single instance
        self.open_files_server = socket.socket(socket.AF_INET,
                                               socket.SOCK_STREAM,
                                               socket.IPPROTO_TCP)

        self.apply_settings()
        self.debug_print("End of MainWindow constructor")