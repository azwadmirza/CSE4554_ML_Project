    def setup(self):
        """Setup main window"""
        logger.info("*** Start of MainWindow setup ***")

        logger.info("Updating PYTHONPATH")
        path_dict = self.get_spyder_pythonpath_dict()
        self.update_python_path(path_dict)

        logger.info("Applying theme configuration...")
        ui_theme = CONF.get('appearance', 'ui_theme')
        color_scheme = CONF.get('appearance', 'selected')

        if ui_theme == 'dark':
            if not running_under_pytest():
                # Set style proxy to fix combobox popup on mac and qdark
                qapp = QApplication.instance()
                qapp.setStyle(self._proxy_style)
            dark_qss = qdarkstyle.load_stylesheet_from_environment()
            self.setStyleSheet(dark_qss)
            self.statusBar().setStyleSheet(dark_qss)
            css_path = DARK_CSS_PATH
        elif ui_theme == 'automatic':
            if not is_dark_font_color(color_scheme):
                if not running_under_pytest():
                    # Set style proxy to fix combobox popup on mac and qdark
                    qapp = QApplication.instance()
                    qapp.setStyle(self._proxy_style)
                dark_qss = qdarkstyle.load_stylesheet_from_environment()
                self.setStyleSheet(dark_qss)
                self.statusBar().setStyleSheet(dark_qss)
                css_path = DARK_CSS_PATH
            else:
                css_path = CSS_PATH
        else:
            css_path = CSS_PATH

        logger.info("Creating core actions...")
        self.close_dockwidget_action = create_action(
            self, icon=ima.icon('close_pane'),
            text=_("Close current pane"),
            triggered=self.close_current_dockwidget,
            context=Qt.ApplicationShortcut
        )
        self.register_shortcut(self.close_dockwidget_action, "_",
                               "Close pane")
        self.lock_interface_action = create_action(
            self,
            _("Lock panes and toolbars"),
            toggled=self.toggle_lock,
            context=Qt.ApplicationShortcut)
        self.register_shortcut(self.lock_interface_action, "_",
                               "Lock unlock panes")
        # custom layouts shortcuts
        self.toggle_next_layout_action = create_action(self,
                                    _("Use next layout"),
                                    triggered=self.toggle_next_layout,
                                    context=Qt.ApplicationShortcut)
        self.toggle_previous_layout_action = create_action(self,
                                    _("Use previous layout"),
                                    triggered=self.toggle_previous_layout,
                                    context=Qt.ApplicationShortcut)
        self.register_shortcut(self.toggle_next_layout_action, "_",
                               "Use next layout")
        self.register_shortcut(self.toggle_previous_layout_action, "_",
                               "Use previous layout")
        # Switcher shortcuts
        self.file_switcher_action = create_action(
                                    self,
                                    _('File switcher...'),
                                    icon=ima.icon('filelist'),
                                    tip=_('Fast switch between files'),
                                    triggered=self.open_switcher,
                                    context=Qt.ApplicationShortcut)
        self.register_shortcut(self.file_switcher_action, context="_",
                               name="File switcher")
        self.symbol_finder_action = create_action(
                                    self, _('Symbol finder...'),
                                    icon=ima.icon('symbol_find'),
                                    tip=_('Fast symbol search in file'),
                                    triggered=self.open_symbolfinder,
                                    context=Qt.ApplicationShortcut)
        self.register_shortcut(self.symbol_finder_action, context="_",
                               name="symbol finder", add_shortcut_to_tip=True)
        self.file_toolbar_actions = [self.file_switcher_action,
                                     self.symbol_finder_action]

        def create_edit_action(text, tr_text, icon):
            textseq = text.split(' ')
            method_name = textseq[0].lower()+"".join(textseq[1:])
            action = create_action(self, tr_text,
                                   icon=icon,
                                   triggered=self.global_callback,
                                   data=method_name,
                                   context=Qt.WidgetShortcut)
            self.register_shortcut(action, "Editor", text)
            return action

        self.undo_action = create_edit_action('Undo', _('Undo'),
                                              ima.icon('undo'))
        self.redo_action = create_edit_action('Redo', _('Redo'),
                                              ima.icon('redo'))
        self.copy_action = create_edit_action('Copy', _('Copy'),
                                              ima.icon('editcopy'))
        self.cut_action = create_edit_action('Cut', _('Cut'),
                                             ima.icon('editcut'))
        self.paste_action = create_edit_action('Paste', _('Paste'),
                                               ima.icon('editpaste'))
        self.selectall_action = create_edit_action("Select All",
                                                   _("Select All"),
                                                   ima.icon('selectall'))

        self.edit_menu_actions = [self.undo_action, self.redo_action,
                                  None, self.cut_action, self.copy_action,
                                  self.paste_action, self.selectall_action]

        logger.info("Creating toolbars...")
        # File menu/toolbar
        self.file_menu = self.menuBar().addMenu(_("&File"))
        self.file_toolbar = self.create_toolbar(_("File toolbar"),
                                                "file_toolbar")
        # Edit menu/toolbar
        self.edit_menu = self.menuBar().addMenu(_("&Edit"))
        self.edit_toolbar = self.create_toolbar(_("Edit toolbar"),
                                                "edit_toolbar")
        # Search menu/toolbar
        self.search_menu = self.menuBar().addMenu(_("&Search"))
        self.search_toolbar = self.create_toolbar(_("Search toolbar"),
                                                   "search_toolbar")
        # Source menu/toolbar
        self.source_menu = self.menuBar().addMenu(_("Sour&ce"))
        self.source_toolbar = self.create_toolbar(_("Source toolbar"),
                                                    "source_toolbar")
        self.source_menu.aboutToShow.connect(self.update_source_menu)

        # Run menu/toolbar
        self.run_menu = self.menuBar().addMenu(_("&Run"))
        self.run_toolbar = self.create_toolbar(_("Run toolbar"),
                                                "run_toolbar")

        # Debug menu/toolbar
        self.debug_menu = self.menuBar().addMenu(_("&Debug"))
        self.debug_toolbar = self.create_toolbar(_("Debug toolbar"),
                                                    "debug_toolbar")

        # Consoles menu/toolbar
        self.consoles_menu = self.menuBar().addMenu(_("C&onsoles"))
        self.consoles_menu.aboutToShow.connect(
                self.update_execution_state_kernel)

        # Projects menu
        self.projects_menu = self.menuBar().addMenu(_("&Projects"))
        self.projects_menu.aboutToShow.connect(self.valid_project)

        # Tools menu
        self.tools_menu = self.menuBar().addMenu(_("&Tools"))

        # View menu
        self.view_menu = self.menuBar().addMenu(_("&View"))

        # Help menu
        self.help_menu = self.menuBar().addMenu(_("&Help"))

        # Status bar
        status = self.statusBar()
        status.setObjectName("StatusBar")
        status.showMessage(_("Welcome to Spyder!"), 5000)

        logger.info("Creating Tools menu...")
        # Tools + External Tools
        prefs_action = create_action(self, _("Pre&ferences"),
                                     icon=ima.icon('configure'),
                                     triggered=self.show_preferences,
                                     context=Qt.ApplicationShortcut)
        self.register_shortcut(prefs_action, "_", "Preferences",
                               add_shortcut_to_tip=True)
        spyder_path_action = create_action(self,
                                _("PYTHONPATH manager"),
                                None, icon=ima.icon('pythonpath'),
                                triggered=self.show_path_manager,
                                tip=_("PYTHONPATH manager"),
                                menurole=QAction.ApplicationSpecificRole)
        reset_spyder_action = create_action(
            self, _("Reset Spyder to factory defaults"),
            triggered=self.reset_spyder)
        self.tools_menu_actions = [prefs_action, spyder_path_action]
        if WinUserEnvDialog is not None:
            winenv_action = create_action(self,
                    _("Current user environment variables..."),
                    icon='win_env.png',
                    tip=_("Show and edit current user environment "
                            "variables in Windows registry "
                            "(i.e. for all sessions)"),
                    triggered=self.win_env)
            self.tools_menu_actions.append(winenv_action)
        from spyder.plugins.completion.kite.utils.install import (
            check_if_kite_installed)
        is_kite_installed, kite_path = check_if_kite_installed()
        if not is_kite_installed:
            install_kite_action = create_action(
                self, _("Install Kite completion engine"),
                icon=get_icon('kite', adjust_for_interface=True),
                triggered=self.show_kite_installation)
            self.tools_menu_actions.append(install_kite_action)
        self.tools_menu_actions += [MENU_SEPARATOR, reset_spyder_action]
        if get_debug_level() >= 3:
            self.menu_lsp_logs = QMenu(_("LSP logs"))
            self.menu_lsp_logs.aboutToShow.connect(self.update_lsp_logs)
            self.tools_menu_actions += [self.menu_lsp_logs]
        # External Tools submenu
        self.external_tools_menu = QMenu(_("External Tools"))
        self.external_tools_menu_actions = []

        # WinPython control panel
        self.wp_action = create_action(self, _("WinPython control panel"),
                    icon=get_icon('winpython.svg'),
                    triggered=lambda:
                    programs.run_python_script('winpython', 'controlpanel'))
        if os.name == 'nt' and is_module_installed('winpython'):
            self.external_tools_menu_actions.append(self.wp_action)

        # Qt-related tools
        additact = []
        for name in ("designer-qt4", "designer"):
            qtdact = create_program_action(self, _("Qt Designer"), name)
            if qtdact:
                break
        for name in ("linguist-qt4", "linguist"):
            qtlact = create_program_action(self, _("Qt Linguist"), "linguist")
            if qtlact:
                break
        args = ['-no-opengl'] if os.name == 'nt' else []
        for act in (qtdact, qtlact):
            if act:
                additact.append(act)
        if additact and is_module_installed('winpython'):
            self.external_tools_menu_actions += [None] + additact

        # Guidata and Sift
        logger.info("Creating guidata and sift entries...")
        gdgq_act = []
        # Guidata and Guiqwt don't support PyQt5 yet and they fail
        # with an AssertionError when imported using those bindings
        # (see spyder-ide/spyder#2274)
        try:
            from guidata import configtools
            from guidata import config       # analysis:ignore
            guidata_icon = configtools.get_icon('guidata.svg')
            guidata_act = create_python_script_action(self,
                                    _("guidata examples"), guidata_icon,
                                    "guidata",
                                    osp.join("tests", "__init__"))
            gdgq_act += [guidata_act]
        except:
            pass
        try:
            from guidata import configtools
            from guiqwt import config  # analysis:ignore
            guiqwt_icon = configtools.get_icon('guiqwt.svg')
            guiqwt_act = create_python_script_action(self,
                            _("guiqwt examples"), guiqwt_icon, "guiqwt",
                            osp.join("tests", "__init__"))
            if guiqwt_act:
                gdgq_act += [guiqwt_act]
            sift_icon = configtools.get_icon('sift.svg')
            sift_act = create_python_script_action(self, _("Sift"),
                        sift_icon, "guiqwt", osp.join("tests", "sift"))
            if sift_act:
                gdgq_act += [sift_act]
        except:
            pass
        if gdgq_act:
            self.external_tools_menu_actions += [None] + gdgq_act

        # Maximize current plugin
        self.maximize_action = create_action(self, '',
                                        triggered=self.maximize_dockwidget,
                                        context=Qt.ApplicationShortcut)
        self.register_shortcut(self.maximize_action, "_", "Maximize pane")
        self.__update_maximize_action()

        # Fullscreen mode
        self.fullscreen_action = create_action(self,
                                        _("Fullscreen mode"),
                                        triggered=self.toggle_fullscreen,
                                        context=Qt.ApplicationShortcut)
        if sys.platform == 'darwin':
            self.fullscreen_action.setEnabled(False)
            self.fullscreen_action.setToolTip(_("For fullscreen mode use "
                                               "macOS built-in feature"))
        else:
            self.register_shortcut(
                self.fullscreen_action,
                "_",
                "Fullscreen mode",
                add_shortcut_to_tip=True
            )

        # Main toolbar
        self.main_toolbar_actions = [self.maximize_action,
                                     self.fullscreen_action,
                                     None,
                                     prefs_action, spyder_path_action]

        self.main_toolbar = self.create_toolbar(_("Main toolbar"),
                                                "main_toolbar")

        # Switcher instance
        logger.info("Loading switcher...")
        self.create_switcher()

        # Internal console plugin
        logger.info("Loading internal console...")
        from spyder.plugins.console.plugin import Console
        self.console = Console(self, namespace=None, exitfunc=self.closing,
                            profile=self.profile,
                            multithreaded=self.multithreaded,
                            message=_("Spyder Internal Console\n\n"
                                    "This console is used to report application\n"
                                    "internal errors and to inspect Spyder\n"
                                    "internals with the following commands:\n"
                                    "  spy.app, spy.window, dir(spy)\n\n"
                                    "Please don't use it to run your code\n\n"))
        self.console.register_plugin()

        # Code completion client initialization
        self.set_splash(_("Starting code completion manager..."))
        from spyder.plugins.completion.plugin import CompletionManager
        self.completions = CompletionManager(self)
        self.completions.start()

        # Working directory plugin
        logger.info("Loading working directory...")
        from spyder.plugins.workingdirectory.plugin import WorkingDirectory
        self.workingdirectory = WorkingDirectory(self, self.init_workdir, main=self)
        self.workingdirectory.register_plugin()
        self.toolbarslist.append(self.workingdirectory.toolbar)

        # Help plugin
        if CONF.get('help', 'enable'):
            self.set_splash(_("Loading help..."))
            from spyder.plugins.help.plugin import Help
            self.help = Help(self, css_path=css_path)
            self.help.register_plugin()

        # Outline explorer widget
        if CONF.get('outline_explorer', 'enable'):
            self.set_splash(_("Loading outline explorer..."))
            from spyder.plugins.outlineexplorer.plugin import OutlineExplorer
            self.outlineexplorer = OutlineExplorer(self)
            self.outlineexplorer.register_plugin()

        from spyder.widgets.status import InterpreterStatus
        self.interpreter_status = InterpreterStatus(
            self,
            status,
            icon=ima.icon('environment'),
        )
        self.interpreter_status.update_interpreter(self.get_main_interpreter())

        # Editor plugin
        self.set_splash(_("Loading editor..."))
        from spyder.plugins.editor.plugin import Editor
        self.editor = Editor(self)
        self.editor.register_plugin()

        # Populating file menu entries
        quit_action = create_action(self, _("&Quit"),
                                    icon=ima.icon('exit'),
                                    tip=_("Quit"),
                                    triggered=self.console.quit,
                                    context=Qt.ApplicationShortcut)
        self.register_shortcut(quit_action, "_", "Quit")
        restart_action = create_action(self, _("&Restart"),
                                       icon=ima.icon('restart'),
                                       tip=_("Restart"),
                                       triggered=self.restart,
                                       context=Qt.ApplicationShortcut)
        self.register_shortcut(restart_action, "_", "Restart")

        file_actions = [
            self.file_switcher_action,
            self.symbol_finder_action,
            None,
        ]
        if sys.platform == 'darwin':
            file_actions.extend(self.editor.tab_navigation_actions + [None])

        file_actions.extend([restart_action, quit_action])
        self.file_menu_actions += file_actions
        self.set_splash("")

        # Namespace browser
        self.set_splash(_("Loading namespace browser..."))
        from spyder.plugins.variableexplorer.plugin import VariableExplorer
        self.variableexplorer = VariableExplorer(self)
        self.variableexplorer.register_plugin()

        # Figure browser
        self.set_splash(_("Loading figure browser..."))
        from spyder.plugins.plots.plugin import Plots
        self.plots = Plots(self)
        self.plots.register_plugin()

        # History log widget
        if CONF.get('historylog', 'enable'):
            self.set_splash(_("Loading history plugin..."))
            from spyder.plugins.history.plugin import HistoryLog
            self.historylog = HistoryLog(self)
            self.historylog.register_plugin()

        # IPython console
        self.set_splash(_("Loading IPython console..."))
        from spyder.plugins.ipythonconsole.plugin import IPythonConsole
        self.ipyconsole = IPythonConsole(self, css_path=css_path)
        self.ipyconsole.register_plugin()

        # Explorer
        if CONF.get('explorer', 'enable'):
            self.set_splash(_("Loading file explorer..."))
            from spyder.plugins.explorer.plugin import Explorer
            self.explorer = Explorer(self)
            self.explorer.register_plugin()

        # Online help widget
        if CONF.get('onlinehelp', 'enable'):
            self.set_splash(_("Loading online help..."))
            from spyder.plugins.onlinehelp.plugin import OnlineHelp
            self.onlinehelp = OnlineHelp(self)
            self.onlinehelp.register_plugin()

        # Project explorer widget
        self.set_splash(_("Loading project explorer..."))
        from spyder.plugins.projects.plugin import Projects
        self.projects = Projects(self)
        self.projects.register_plugin()
        self.project_path = self.projects.get_pythonpath(at_start=True)

        # Find in files
        if CONF.get('find_in_files', 'enable'):
            from spyder.plugins.findinfiles.plugin import FindInFiles
            self.findinfiles = FindInFiles(self)
            self.findinfiles.register_plugin()

        # Load other plugins (former external plugins)
        # TODO: Use this bucle to load all internall plugins and remove
        # duplicated code
        other_plugins = ['breakpoints', 'profiler', 'pylint']
        for plugin_name in other_plugins:
            if CONF.get(plugin_name, 'enable'):
                module = importlib.import_module(
                        'spyder.plugins.{}'.format(plugin_name))
                plugin = module.PLUGIN_CLASS(self)
                if plugin.check_compatibility()[0]:
                    self.thirdparty_plugins.append(plugin)
                    plugin.register_plugin()

        # Third-party plugins
        from spyder import dependencies

        self.set_splash(_("Loading third-party plugins..."))
        for mod in get_spyderplugins_mods():
            try:
                plugin = mod.PLUGIN_CLASS(self)
                if plugin.check_compatibility()[0]:
                    if hasattr(plugin, 'COMPLETION_CLIENT_NAME'):
                        self.completions.register_completion_plugin(plugin)
                    else:
                        self.thirdparty_plugins.append(plugin)
                        plugin.register_plugin()

                    # Add to dependencies dialog
                    module = mod.__name__
                    name = module.replace('_', '-')
                    if plugin.DESCRIPTION:
                        description = plugin.DESCRIPTION
                    else:
                        description = plugin.get_plugin_title()

                    dependencies.add(module, name, description,
                                     '', None, kind=dependencies.PLUGIN)

            except Exception as error:
                print("%s: %s" % (mod, str(error)), file=STDERR)
                traceback.print_exc(file=STDERR)

        self.set_splash(_("Setting up main window..."))

        # Help menu
        trouble_action = create_action(self,
                                        _("Troubleshooting..."),
                                        triggered=self.trouble_guide)
        dep_action = create_action(self, _("Dependencies..."),
                                    triggered=self.show_dependencies,
                                    icon=ima.icon('advanced'))
        report_action = create_action(self,
                                        _("Report issue..."),
                                        icon=ima.icon('bug'),
                                        triggered=self.report_issue)
        support_action = create_action(self,
                                        _("Spyder support..."),
                                        triggered=self.google_group)
        self.check_updates_action = create_action(self,
                                                _("Check for updates..."),
                                                triggered=self.check_updates)

        # Spyder documentation
        doc_action = create_action(self, _("Spyder documentation"),
                                   icon=ima.icon('DialogHelpButton'),
                                   triggered=lambda:
                                   programs.start_file(__docs_url__))
        self.register_shortcut(doc_action, "_",
                               "spyder documentation")

        spyder_vid = ("https://www.youtube.com/playlist"
                      "?list=PLPonohdiDqg9epClEcXoAPUiK0pN5eRoc")
        vid_action = create_action(self, _("Tutorial videos"),
                                   icon=ima.icon('VideoIcon'),
                                   triggered=lambda:
                                   programs.start_file(spyder_vid))

        shortcuts_action = create_action(self, _("Shortcuts Summary"),
                                         shortcut="Meta+F1",
                                         triggered=self.show_shortcuts_dialog)

        #----- Tours
        self.tour = tour.AnimatedTour(self)
        # self.tours_menu = QMenu(_("Interactive tours"), self)
        # self.tour_menu_actions = []
        # # TODO: Only show intro tour for now. When we are close to finish
        # # 3.0, we will finish and show the other tour
        self.tours_available = tour.get_tours(DEFAULT_TOUR)

        for i, tour_available in enumerate(self.tours_available):
            self.tours_available[i]['last'] = 0
            tour_name = tour_available['name']

        #     def trigger(i=i, self=self):  # closure needed!
        #         return lambda: self.show_tour(i)

        #     temp_action = create_action(self, tour_name, tip="",
        #                                 triggered=trigger())
        #     self.tour_menu_actions += [temp_action]

        # self.tours_menu.addActions(self.tour_menu_actions)
        self.tour_action = create_action(
            self, self.tours_available[DEFAULT_TOUR]['name'],
            tip=_("Interactive tour introducing Spyder's panes and features"),
            triggered=lambda: self.show_tour(DEFAULT_TOUR))

        self.help_menu_actions = [doc_action, vid_action, shortcuts_action,
                                  self.tour_action,
                                  MENU_SEPARATOR, trouble_action,
                                  report_action, dep_action,
                                  self.check_updates_action, support_action,
                                  MENU_SEPARATOR]
        # Python documentation
        if get_python_doc_path() is not None:
            pydoc_act = create_action(self, _("Python documentation"),
                                triggered=lambda:
                                programs.start_file(get_python_doc_path()))
            self.help_menu_actions.append(pydoc_act)
        # IPython documentation
        if self.help is not None:
            ipython_menu = QMenu(_("IPython documentation"), self)
            intro_action = create_action(self, _("Intro to IPython"),
                                        triggered=self.ipyconsole.show_intro)
            quickref_action = create_action(self, _("Quick reference"),
                                    triggered=self.ipyconsole.show_quickref)
            guiref_action = create_action(self, _("Console help"),
                                        triggered=self.ipyconsole.show_guiref)
            add_actions(ipython_menu, (intro_action, guiref_action,
                                        quickref_action))
            self.help_menu_actions.append(ipython_menu)
        # Windows-only: documentation located in sys.prefix/Doc
        ipm_actions = []
        def add_ipm_action(text, path):
            """Add installed Python module doc action to help submenu"""
            # QAction.triggered works differently for PySide and PyQt
            path = file_uri(path)
            if not API == 'pyside':
                slot=lambda _checked, path=path: programs.start_file(path)
            else:
                slot=lambda path=path: programs.start_file(path)
            action = create_action(self, text,
                    icon='%s.png' % osp.splitext(path)[1][1:],
                    triggered=slot)
            ipm_actions.append(action)
        sysdocpth = osp.join(sys.prefix, 'Doc')
        if osp.isdir(sysdocpth): # exists on Windows, except frozen dist.
            for docfn in os.listdir(sysdocpth):
                pt = r'([a-zA-Z\_]*)(doc)?(-dev)?(-ref)?(-user)?.(chm|pdf)'
                match = re.match(pt, docfn)
                if match is not None:
                    pname = match.groups()[0]
                    if pname not in ('Python', ):
                        add_ipm_action(pname, osp.join(sysdocpth, docfn))
        # Installed Python modules submenu (Windows only)
        if ipm_actions:
            pymods_menu = QMenu(_("Installed Python modules"), self)
            add_actions(pymods_menu, ipm_actions)
            self.help_menu_actions.append(pymods_menu)
        # Online documentation
        web_resources = QMenu(_("Online documentation"), self)
        webres_actions = create_module_bookmark_actions(self,
                                                        self.BOOKMARKS)
        webres_actions.insert(2, None)
        webres_actions.insert(5, None)
        webres_actions.insert(8, None)
        add_actions(web_resources, webres_actions)
        self.help_menu_actions.append(web_resources)
        # Qt assistant link
        if sys.platform.startswith('linux') and not PYQT5:
            qta_exe = "assistant-qt4"
        else:
            qta_exe = "assistant"
        qta_act = create_program_action(self, _("Qt documentation"),
                                        qta_exe)
        if qta_act:
            self.help_menu_actions += [qta_act, None]

        # About Spyder
        about_action = create_action(self,
                                _("About %s...") % "Spyder",
                                icon=ima.icon('MessageBoxInformation'),
                                triggered=self.show_about)
        self.help_menu_actions += [MENU_SEPARATOR, about_action]

        # Status bar widgets
        from spyder.widgets.status import MemoryStatus, CPUStatus, ClockStatus
        self.mem_status = MemoryStatus(self, status)
        self.cpu_status = CPUStatus(self, status)
        self.clock_status = ClockStatus(self, status)
        self.apply_statusbar_settings()

        # ----- View
        # View menu
        self.plugins_menu = QMenu(_("Panes"), self)

        self.toolbars_menu = QMenu(_("Toolbars"), self)
        self.quick_layout_menu = QMenu(_("Window layouts"), self)
        self.quick_layout_set_menu()

        self.view_menu.addMenu(self.plugins_menu)  # Panes
        add_actions(self.view_menu, (self.lock_interface_action,
                                     self.close_dockwidget_action,
                                     self.maximize_action,
                                     MENU_SEPARATOR))
        self.show_toolbars_action = create_action(self,
                                _("Show toolbars"),
                                triggered=self.show_toolbars,
                                context=Qt.ApplicationShortcut)
        self.register_shortcut(self.show_toolbars_action, "_",
                               "Show toolbars")
        self.view_menu.addMenu(self.toolbars_menu)
        self.view_menu.addAction(self.show_toolbars_action)
        add_actions(self.view_menu, (MENU_SEPARATOR,
                                     self.quick_layout_menu,
                                     self.toggle_previous_layout_action,
                                     self.toggle_next_layout_action,
                                     MENU_SEPARATOR,
                                     self.fullscreen_action))
        if set_attached_console_visible is not None:
            cmd_act = create_action(self,
                                _("Attached console window (debugging)"),
                                toggled=set_attached_console_visible)
            cmd_act.setChecked(is_attached_console_visible())
            add_actions(self.view_menu, (MENU_SEPARATOR, cmd_act))

        # Adding external tools action to "Tools" menu
        if self.external_tools_menu_actions:
            external_tools_act = create_action(self, _("External Tools"))
            external_tools_act.setMenu(self.external_tools_menu)
            self.tools_menu_actions += [None, external_tools_act]

        # Filling out menu/toolbar entries:
        add_actions(self.file_menu, self.file_menu_actions)
        add_actions(self.edit_menu, self.edit_menu_actions)
        add_actions(self.search_menu, self.search_menu_actions)
        add_actions(self.source_menu, self.source_menu_actions)
        add_actions(self.run_menu, self.run_menu_actions)
        add_actions(self.debug_menu, self.debug_menu_actions)
        add_actions(self.consoles_menu, self.consoles_menu_actions)
        add_actions(self.projects_menu, self.projects_menu_actions)
        add_actions(self.tools_menu, self.tools_menu_actions)
        add_actions(self.external_tools_menu,
                    self.external_tools_menu_actions)
        add_actions(self.help_menu, self.help_menu_actions)

        add_actions(self.main_toolbar, self.main_toolbar_actions)
        add_actions(self.file_toolbar, self.file_toolbar_actions)
        add_actions(self.edit_toolbar, self.edit_toolbar_actions)
        add_actions(self.search_toolbar, self.search_toolbar_actions)
        add_actions(self.source_toolbar, self.source_toolbar_actions)
        add_actions(self.debug_toolbar, self.debug_toolbar_actions)
        add_actions(self.run_toolbar, self.run_toolbar_actions)

        # Apply all defined shortcuts (plugins + 3rd-party plugins)
        self.apply_shortcuts()

        # Emitting the signal notifying plugins that main window menu and
        # toolbar actions are all defined:
        self.all_actions_defined.emit()

        # Window set-up
        logger.info("Setting up window...")
        self.setup_layout(default=False)

        # Enabling tear off for all menus except help menu
        if CONF.get('main', 'tear_off_menus'):
            for child in self.menuBar().children():
                if isinstance(child, QMenu) and child != self.help_menu:
                    child.setTearOffEnabled(True)

        # Menu about to show
        for child in self.menuBar().children():
            if isinstance(child, QMenu):
                try:
                    child.aboutToShow.connect(self.update_edit_menu)
                    child.aboutToShow.connect(self.update_search_menu)
                except TypeError:
                    pass

        logger.info("*** End of MainWindow setup ***")
        self.is_starting_up = False