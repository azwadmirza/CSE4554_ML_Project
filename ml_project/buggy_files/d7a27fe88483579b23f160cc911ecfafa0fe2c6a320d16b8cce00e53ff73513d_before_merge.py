    def setup(self):
        """Setup main window"""
        self.debug_print("*** Start of MainWindow setup ***")
        if not self.light:
            self.debug_print("  ..core actions")
            self.close_dockwidget_action = create_action(self,
                                        _("Close current pane"),
                                        triggered=self.close_current_dockwidget,
                                        context=Qt.ApplicationShortcut)
            self.register_shortcut(self.close_dockwidget_action, "_",
                                   "Close pane")

            # custom layouts shortcuts
            self.toggle_next_layout_action = create_action(self,
                                        _("Toggle next layout"),
                                        triggered=self.toggle_next_layout,
                                        context=Qt.ApplicationShortcut)
            self.toggle_previous_layout_action = create_action(self,
                                        _("Toggle previous layout"),
                                        triggered=self.toggle_previous_layout,
                                        context=Qt.ApplicationShortcut)
            self.register_shortcut(self.toggle_next_layout_action, "_",
                                   "Toggle next layout")
            self.register_shortcut(self.toggle_previous_layout_action, "_",
                                   "Toggle previous layout")


            _text = _("&Find text")
            self.find_action = create_action(self, _text, icon='find.png',
                                             tip=_text, triggered=self.find,
                                             context=Qt.WidgetShortcut)
            self.register_shortcut(self.find_action, "Editor", "Find text")
            self.find_next_action = create_action(self, _("Find &next"),
                  icon='findnext.png', triggered=self.find_next,
                  context=Qt.WidgetShortcut)
            self.register_shortcut(self.find_next_action, "Editor",
                                   "Find next")
            self.find_previous_action = create_action(self,
                        _("Find &previous"),
                        icon='findprevious.png', triggered=self.find_previous,
                        context=Qt.WidgetShortcut)
            self.register_shortcut(self.find_previous_action, "Editor",
                                   "Find previous")
            _text = _("&Replace text")
            self.replace_action = create_action(self, _text, icon='replace.png',
                                            tip=_text, triggered=self.replace,
                                            context=Qt.WidgetShortcut)
            self.register_shortcut(self.replace_action, "Editor",
                                   "Replace text")
            def create_edit_action(text, tr_text, icon_name):
                textseq = text.split(' ')
                method_name = textseq[0].lower()+"".join(textseq[1:])
                return create_action(self, tr_text,
                                     shortcut=keybinding(text.replace(' ', '')),
                                     icon=get_icon(icon_name),
                                     triggered=self.global_callback,
                                     data=method_name,
                                     context=Qt.WidgetShortcut)
            self.undo_action = create_edit_action("Undo", _("Undo"),
                                                  'undo.png')
            self.redo_action = create_edit_action("Redo", _("Redo"), 'redo.png')
            self.copy_action = create_edit_action("Copy", _("Copy"),
                                                  'editcopy.png')
            self.cut_action = create_edit_action("Cut", _("Cut"), 'editcut.png')
            self.paste_action = create_edit_action("Paste", _("Paste"),
                                                   'editpaste.png')
            self.delete_action = create_edit_action("Delete", _("Delete"),
                                                    'editdelete.png')
            self.selectall_action = create_edit_action("Select All",
                                                       _("Select All"),
                                                       'selectall.png')
            self.edit_menu_actions = [self.undo_action, self.redo_action,
                                      None, self.cut_action, self.copy_action,
                                      self.paste_action, self.delete_action,
                                      None, self.selectall_action]
            self.search_menu_actions = [self.find_action, self.find_next_action,
                                        self.find_previous_action,
                                        self.replace_action]
            self.search_toolbar_actions = [self.find_action,
                                           self.find_next_action,
                                           self.replace_action]

        namespace = None
        if not self.light:
            self.debug_print("  ..toolbars")
            # File menu/toolbar
            self.file_menu = self.menuBar().addMenu(_("&File"))
            self.file_menu.aboutToShow.connect(self.update_file_menu)
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


            self.debug_print("  ..tools")
            # Tools + External Tools
            prefs_action = create_action(self, _("Pre&ferences"),
                                         icon='configure.png',
                                         triggered=self.edit_preferences)
            self.register_shortcut(prefs_action, "_", "Preferences")
            add_shortcut_to_tooltip(prefs_action, context="_",
                                    name="Preferences")
            spyder_path_action = create_action(self,
                                    _("PYTHONPATH manager"),
                                    None, 'pythonpath_mgr.png',
                                    triggered=self.path_manager_callback,
                                    tip=_("Python Path Manager"),
                                    menurole=QAction.ApplicationSpecificRole)
            update_modules_action = create_action(self,
                                        _("Update module names list"),
                                        triggered=lambda:
                                                  module_completion.reset(),
                                        tip=_("Refresh list of module names "
                                              "available in PYTHONPATH"))
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
            self.tools_menu_actions += [None, update_modules_action]

            # External Tools submenu
            self.external_tools_menu = QMenu(_("External Tools"))
            self.external_tools_menu_actions = []
            # Python(x,y) launcher
            self.xy_action = create_action(self,
                                   _("Python(x,y) launcher"),
                                   icon=get_icon('pythonxy.png'),
                                   triggered=lambda:
                                   programs.run_python_script('xy', 'xyhome'))
            if os.name == 'nt' and is_module_installed('xy'):
                self.external_tools_menu_actions.append(self.xy_action)
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
                qtdact = create_program_action(self, _("Qt Designer"),
                                               name, 'qtdesigner.png')
                if qtdact:
                    break
            for name in ("linguist-qt4", "linguist"):
                qtlact = create_program_action(self, _("Qt Linguist"),
                                               "linguist", 'qtlinguist.png')
                if qtlact:
                    break
            args = ['-no-opengl'] if os.name == 'nt' else []
            qteact = create_python_script_action(self,
                                   _("Qt examples"), 'qt.png', "PyQt4",
                                   osp.join("examples", "demos",
                                            "qtdemo", "qtdemo"), args)
            for act in (qtdact, qtlact, qteact):
                if act:
                    additact.append(act)
            if additact and (is_module_installed('winpython') or \
              is_module_installed('xy')):
                self.external_tools_menu_actions += [None] + additact

            # Guidata and Sift
            self.debug_print("  ..sift?")
            gdgq_act = []
            if is_module_installed('guidata'):
                from guidata import configtools
                from guidata import config  # (loading icons) analysis:ignore
                guidata_icon = configtools.get_icon('guidata.svg')
                guidata_act = create_python_script_action(self,
                               _("guidata examples"), guidata_icon, "guidata",
                               osp.join("tests", "__init__"))
                if guidata_act:
                    gdgq_act += [guidata_act]
                if is_module_installed('guiqwt'):
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
            if gdgq_act:
                self.external_tools_menu_actions += [None] + gdgq_act

            # ViTables
            vitables_act = create_program_action(self, _("ViTables"),
                                                 "vitables", 'vitables.png')
            if vitables_act:
                self.external_tools_menu_actions += [None, vitables_act]

            # Maximize current plugin
            self.maximize_action = create_action(self, '',
                                            triggered=self.maximize_dockwidget)
            self.register_shortcut(self.maximize_action, "_",
                                   "Maximize pane")
            self.__update_maximize_action()

            # Fullscreen mode
            self.fullscreen_action = create_action(self,
                                            _("Fullscreen mode"),
                                            triggered=self.toggle_fullscreen)
            self.register_shortcut(self.fullscreen_action, "_",
                                   "Fullscreen mode")
            add_shortcut_to_tooltip(self.fullscreen_action, context="_",
                                    name="Fullscreen mode")

            # Main toolbar
            self.main_toolbar_actions = [self.maximize_action,
                                         self.fullscreen_action, None,
                                         prefs_action, spyder_path_action]

            self.main_toolbar = self.create_toolbar(_("Main toolbar"),
                                                    "main_toolbar")

            # Internal console plugin
            self.debug_print("  ..plugin: internal console")
            from spyderlib.plugins.console import Console
            self.console = Console(self, namespace, exitfunc=self.closing,
                              profile=self.profile,
                              multithreaded=self.multithreaded,
                              message=_("Spyder Internal Console\n\n"
                                        "This console is used to report application\n"
                                        "internal errors and to inspect Spyder\n"
                                        "internals with the following commands:\n"
                                        "  spy.app, spy.window, dir(spy)\n\n"
                                        "Please don't use it to run your code\n\n"))
            self.console.register_plugin()

            # Working directory plugin
            self.debug_print("  ..plugin: working directory")
            from spyderlib.plugins.workingdirectory import WorkingDirectory
            self.workingdirectory = WorkingDirectory(self, self.init_workdir, main=self)
            self.workingdirectory.register_plugin()
            self.toolbarslist.append(self.workingdirectory)

            # Object inspector plugin
            if CONF.get('inspector', 'enable'):
                self.set_splash(_("Loading object inspector..."))
                from spyderlib.plugins.inspector import ObjectInspector
                self.inspector = ObjectInspector(self)
                self.inspector.register_plugin()

            # Outline explorer widget
            if CONF.get('outline_explorer', 'enable'):
                self.set_splash(_("Loading outline explorer..."))
                from spyderlib.plugins.outlineexplorer import OutlineExplorer
                fullpath_sorting = CONF.get('editor', 'fullpath_sorting', True)
                self.outlineexplorer = OutlineExplorer(self,
                                            fullpath_sorting=fullpath_sorting)
                self.outlineexplorer.register_plugin()

            # Editor plugin
            self.set_splash(_("Loading editor..."))
            from spyderlib.plugins.editor import Editor
            self.editor = Editor(self)
            self.editor.register_plugin()

            # Populating file menu entries
            quit_action = create_action(self, _("&Quit"),
                                        icon='exit.png', tip=_("Quit"),
                                        triggered=self.console.quit)
            self.register_shortcut(quit_action, "_", "Quit")
            self.file_menu_actions += [self.load_temp_session_action,
                                       self.load_session_action,
                                       self.save_session_action,
                                       None, quit_action]
            self.set_splash("")

            self.debug_print("  ..widgets")
            # Find in files
            if CONF.get('find_in_files', 'enable'):
                from spyderlib.plugins.findinfiles import FindInFiles
                self.findinfiles = FindInFiles(self)
                self.findinfiles.register_plugin()

            # Explorer
            if CONF.get('explorer', 'enable'):
                self.set_splash(_("Loading file explorer..."))
                from spyderlib.plugins.explorer import Explorer
                self.explorer = Explorer(self)
                self.explorer.register_plugin()

            # History log widget
            if CONF.get('historylog', 'enable'):
                self.set_splash(_("Loading history plugin..."))
                from spyderlib.plugins.history import HistoryLog
                self.historylog = HistoryLog(self)
                self.historylog.register_plugin()

            # Online help widget
            try:    # Qt >= v4.4
                from spyderlib.plugins.onlinehelp import OnlineHelp
            except ImportError:    # Qt < v4.4
                OnlineHelp = None  # analysis:ignore
            if CONF.get('onlinehelp', 'enable') and OnlineHelp is not None:
                self.set_splash(_("Loading online help..."))
                self.onlinehelp = OnlineHelp(self)
                self.onlinehelp.register_plugin()

            # Project explorer widget
            if CONF.get('project_explorer', 'enable'):
                self.set_splash(_("Loading project explorer..."))
                from spyderlib.plugins.projectexplorer import ProjectExplorer
                self.projectexplorer = ProjectExplorer(self)
                self.projectexplorer.register_plugin()

        # External console
        if self.light:
            # This is necessary to support the --working-directory option:
            if self.init_workdir is not None:
                os.chdir(self.init_workdir)
        else:
            self.set_splash(_("Loading external console..."))
        from spyderlib.plugins.externalconsole import ExternalConsole
        self.extconsole = ExternalConsole(self, light_mode=self.light)
        self.extconsole.register_plugin()

        # Namespace browser
        if not self.light:
            # In light mode, namespace browser is opened inside external console
            # Here, it is opened as an independent plugin, in its own dockwidget
            self.set_splash(_("Loading namespace browser..."))
            from spyderlib.plugins.variableexplorer import VariableExplorer
            self.variableexplorer = VariableExplorer(self)
            self.variableexplorer.register_plugin()

        # IPython console
        if IPYTHON_QT_INSTALLED and not self.light:
            self.set_splash(_("Loading IPython console..."))
            from spyderlib.plugins.ipythonconsole import IPythonConsole
            self.ipyconsole = IPythonConsole(self)
            self.ipyconsole.register_plugin()

        if not self.light:
            nsb = self.variableexplorer.add_shellwidget(self.console.shell)
            self.console.shell.refresh.connect(nsb.refresh_table)
            nsb.auto_refresh_button.setEnabled(False)

            self.set_splash(_("Setting up main window..."))

            # Help menu            
            dep_action = create_action(self, _("Optional dependencies..."),
                                       triggered=self.show_dependencies,
                                       icon='advanced.png')
            report_action = create_action(self,
                                          _("Report issue..."),
                                          icon=get_icon('bug.png'),
                                          triggered=self.report_issue)
            support_action = create_action(self,
                                           _("Spyder support..."),
                                           triggered=self.google_group)
            # Spyder documentation
            doc_path = get_module_data_path('spyderlib', relpath="doc",
                                            attr_name='DOCPATH')
            # * Trying to find the chm doc
            spyder_doc = osp.join(doc_path, "Spyderdoc.chm")
            if not osp.isfile(spyder_doc):
                spyder_doc = osp.join(doc_path, os.pardir, "Spyderdoc.chm")
            # * Trying to find the html doc
            if not osp.isfile(spyder_doc):
                spyder_doc = osp.join(doc_path, "index.html")
            # * Trying to find the development-version html doc
            if not osp.isfile(spyder_doc):
                spyder_doc = osp.join(get_module_source_path('spyderlib'),
                                      os.pardir, 'build', 'lib', 'spyderlib',
                                      'doc', "index.html")
            # * If we totally fail, point to our web build
            if not osp.isfile(spyder_doc):
                spyder_doc = 'http://pythonhosted.org/spyder'
            else:
                spyder_doc = file_uri(spyder_doc)
            doc_action = create_action( self, _("Spyder documentation"), shortcut="F1", 
                                       icon=get_std_icon('DialogHelpButton'),
                                       triggered=lambda : programs.start_file(spyder_doc))

            tut_action = create_action(self, _("Spyder tutorial"),
                                       triggered=self.inspector.show_tutorial)

        #----- Tours
            self.tour = tour.AnimatedTour(self)
            self.tours_menu = QMenu(_("Spyder tours"))
            self.tour_menu_actions = []
            self.tours_available = tour.get_tours()

            for i, tour_available in enumerate(self.tours_available):
                self.tours_available[i]['last'] = 0
                tour_name = tour_available['name']

                def trigger(i=i, self=self):  # closure needed!
                    return lambda: self.show_tour(i)

                temp_action = create_action(self, tour_name, tip=_(""),
                                            triggered=trigger())
                self.tour_menu_actions += [temp_action]

            self.tours_menu.addActions(self.tour_menu_actions)

            if not DEV:
                self.tours_menu = None

            self.help_menu_actions = [doc_action, tut_action, self.tours_menu,
                                      None,
                                      report_action, dep_action, support_action,
                                      None]
            # Python documentation
            if get_python_doc_path() is not None:
                pydoc_act = create_action(self, _("Python documentation"),
                                  triggered=lambda:
                                  programs.start_file(get_python_doc_path()))
                self.help_menu_actions.append(pydoc_act)
            # IPython documentation
            if self.ipyconsole is not None:
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
                path = file_uri(path)
                action = create_action(self, text,
                       icon='%s.png' % osp.splitext(path)[1][1:],
                       triggered=lambda path=path: programs.start_file(path))
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
            # Documentation provided by Python(x,y), if available
            try:
                from xy.config import DOC_PATH as xy_doc_path
                xydoc = osp.join(xy_doc_path, "Libraries")
                def add_xydoc(text, pathlist):
                    for path in pathlist:
                        if osp.exists(path):
                            add_ipm_action(text, path)
                            break
                add_xydoc(_("Python(x,y) documentation folder"),
                          [xy_doc_path])
                add_xydoc(_("IPython documentation"),
                          [osp.join(xydoc, "IPython", "ipythondoc.chm")])
                add_xydoc(_("guidata documentation"),
                          [osp.join(xydoc, "guidata", "guidatadoc.chm"),
                           r"D:\Python\guidata\build\doc_chm\guidatadoc.chm"])
                add_xydoc(_("guiqwt documentation"),
                          [osp.join(xydoc, "guiqwt", "guiqwtdoc.chm"),
                           r"D:\Python\guiqwt\build\doc_chm\guiqwtdoc.chm"])
                add_xydoc(_("Matplotlib documentation"),
                          [osp.join(xydoc, "matplotlib", "Matplotlibdoc.chm"),
                           osp.join(xydoc, "matplotlib", "Matplotlib.pdf")])
                add_xydoc(_("NumPy documentation"),
                          [osp.join(xydoc, "NumPy", "numpy.chm")])
                add_xydoc(_("NumPy reference guide"),
                          [osp.join(xydoc, "NumPy", "numpy-ref.pdf")])
                add_xydoc(_("NumPy user guide"),
                          [osp.join(xydoc, "NumPy", "numpy-user.pdf")])
                add_xydoc(_("SciPy documentation"),
                          [osp.join(xydoc, "SciPy", "scipy.chm"),
                           osp.join(xydoc, "SciPy", "scipy-ref.pdf")])
            except (ImportError, KeyError, RuntimeError):
                pass
            # Installed Python modules submenu (Windows only)
            if ipm_actions:
                pymods_menu = QMenu(_("Installed Python modules"), self)
                add_actions(pymods_menu, ipm_actions)
                self.help_menu_actions.append(pymods_menu)
            # Online documentation
            web_resources = QMenu(_("Online documentation"))
            webres_actions = create_module_bookmark_actions(self,
                                                            self.BOOKMARKS)
            webres_actions.insert(2, None)
            webres_actions.insert(5, None)
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
                                    icon=get_std_icon('MessageBoxInformation'),
                                    triggered=self.about)
            self.help_menu_actions += [None, about_action]

            # Status bar widgets
            from spyderlib.widgets.status import MemoryStatus, CPUStatus
            self.mem_status = MemoryStatus(self, status)
            self.cpu_status = CPUStatus(self, status)
            self.apply_statusbar_settings()

            # Third-party plugins
            for mod in get_spyderplugins_mods(prefix='p_', extension='.py'):
                try:
                    plugin = mod.PLUGIN_CLASS(self)
                    self.thirdparty_plugins.append(plugin)
                    plugin.register_plugin()
                except AttributeError as error:
                    print("%s: %s" % (mod, str(error)), file=STDERR)


    #----- View
            # View menu
            self.plugins_menu = QMenu(_("Panes"), self)
            self.toolbars_menu = QMenu(_("Toolbars"), self)
            self.view_menu.addMenu(self.plugins_menu)
            self.view_menu.addMenu(self.toolbars_menu)
            self.quick_layout_menu = QMenu(_("Custom window layouts"), self)
            self.quick_layout_set_menu()

            if set_attached_console_visible is not None:
                cmd_act = create_action(self,
                                    _("Attached console window (debugging)"),
                                    toggled=set_attached_console_visible)
                cmd_act.setChecked(is_attached_console_visible())
                add_actions(self.view_menu, (None, cmd_act))
            add_actions(self.view_menu, (None, self.fullscreen_action,
                                         self.maximize_action,
                                         self.close_dockwidget_action, None,
                                         self.toggle_previous_layout_action,
                                         self.toggle_next_layout_action,
                                         self.quick_layout_menu))

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
        #self.remove_deprecated_shortcuts()

        # Emitting the signal notifying plugins that main window menu and
        # toolbar actions are all defined:
        self.all_actions_defined.emit()

        # Window set-up
        self.debug_print("Setting up window...")
        self.setup_layout(default=False)

        self.splash.hide()

        # Enabling tear off for all menus except help menu
        if CONF.get('main', 'tear_off_menus'):
            for child in self.menuBar().children():
                if isinstance(child, QMenu) and child != self.help_menu:
                    child.setTearOffEnabled(True)

        # Menu about to show
        for child in self.menuBar().children():
            if isinstance(child, QMenu):
                child.aboutToShow.connect(self.update_edit_menu)

        self.debug_print("*** End of MainWindow setup ***")
        self.is_starting_up = False