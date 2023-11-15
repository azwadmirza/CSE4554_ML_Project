    def __add_menu(self):
        """Add the menu to the frame

        """
        self.__menu_file = wx.Menu()
        self.__menu_file.Append(
            wx.ID_NEW, "New Project", helpString="Create an empty project"
        )
        self.__menu_file.Append(
            wx.ID_OPEN,
            "Open Project...\tctrl+O",
            helpString="Open a project from a .{} project file".format(
                cellprofiler.preferences.EXT_PROJECT
            ),
        )
        self.recent_workspace_files = wx.Menu()
        self.__menu_file.AppendSubMenu(self.recent_workspace_files, "Open Recent")
        self.__menu_file.Append(
            wx.ID_SAVE,
            "Save Project\tctrl+S",
            helpString="Save the project to the current project file",
        )
        self.__menu_file.Append(
            wx.ID_SAVEAS,
            "Save Project As...",
            helpString="Save the project to a file of your choice",
        )
        self.__menu_file.Append(
            ID_FILE_REVERT_TO_SAVED,
            "Revert to Saved",
            helpString="Reload the project file, discarding changes",
        )
        submenu = wx.Menu()
        submenu.Append(
            ID_FILE_LOAD_PIPELINE,
            "Pipeline from File...",
            "Import a pipeline into the project from a .%s file"
            % cellprofiler.preferences.EXT_PIPELINE,
        )
        submenu.Append(
            ID_FILE_URL_LOAD_PIPELINE,
            "Pipeline from URL...",
            "Load a pipeline from the web",
        )
        submenu.Append(
            ID_FILE_IMPORT_FILE_LIST,
            "File List...",
            "Add files or URLs to the Images module file list",
        )
        self.__menu_file.AppendSubMenu(submenu, "Import")

        submenu = wx.Menu()
        submenu.Append(
            ID_FILE_SAVE_PIPELINE,
            "Pipeline...\tctrl+P",
            "Save the project's pipeline to a .%s file"
            % cellprofiler.preferences.EXT_PIPELINE,
        )
        submenu.Append(
            ID_FILE_EXPORT_IMAGE_SETS,
            "Image Set Listing...",
            "Export the project's image sets as a CSV file suitable for LoadData",
        )
        submenu.Append(
            ID_FILE_EXPORT_PIPELINE_NOTES,
            "Pipeline notes...",
            "Save a text file outlining the pipeline's modules and module notes",
        )
        self.__menu_file.AppendSubMenu(submenu, "Export")
        self.__menu_file.Append(
            ID_FILE_CLEAR_PIPELINE,
            "Clear Pipeline",
            "Remove all modules from the current pipeline",
        )
        self.__menu_file.AppendSeparator()
        self.__menu_file.Append(
            ID_FILE_OPEN_IMAGE, "View Image", "Open an image file for viewing"
        )
        self.__menu_file.AppendSeparator()
        self.__menu_file.Append(
            ID_FILE_ANALYZE_IMAGES,
            "Analyze Images\tctrl+N",
            "Run the pipeline on the images in the image directory",
        )
        self.__menu_file.Append(
            ID_FILE_STOP_ANALYSIS, "Stop Analysis", "Stop running the pipeline"
        )
        self.__menu_file.Append(
            ID_FILE_RUN_MULTIPLE_PIPELINES, "Run Multiple Pipelines"
        )
        if os.name == "posix":
            self.__menu_file.Append(ID_FILE_NEW_CP, "Open a New CP Window")
        self.__menu_file.Append(
            ID_FILE_RESTART,
            "Resume Pipeline",
            "Resume a pipeline from a saved measurements file.",
        )
        self.__menu_file.AppendSeparator()
        self.__menu_file.Append(
            ID_OPTIONS_PREFERENCES,
            "&Preferences...",
            "Set global application preferences",
        )

        self.recent_files = wx.Menu()
        self.recent_pipeline_files = wx.Menu()
        self.__menu_file.Append(ID_FILE_EXIT, "E&xit\tctrl+Q", "Quit the application")

        self.menu_edit = wx.Menu()
        self.menu_edit.Append(wx.ID_UNDO, helpString="Undo last action")
        self.menu_edit.AppendSeparator()

        self.menu_edit.Append(wx.ID_CUT)
        self.menu_edit.Append(wx.ID_COPY)
        self.menu_edit.Append(wx.ID_PASTE)
        self.menu_edit.Append(wx.ID_SELECTALL)

        self.menu_edit.AppendSeparator()
        self.menu_edit.Append(
            ID_EDIT_MOVE_UP,
            "Move Selected Modules &Up",
            "Move selected modules toward the start of the pipeline",
        )
        self.menu_edit.Append(
            ID_EDIT_MOVE_DOWN,
            "Move Selected Modules &Down",
            "Move selected modules toward the end of the pipeline",
        )
        self.menu_edit.Append(
            ID_EDIT_DELETE, "&Delete Selected Modules", "Delete selected modules"
        )
        self.menu_edit.Append(
            ID_EDIT_DUPLICATE, "Duplicate Selected Modules", "Duplicate selected modules"
        )
        self.menu_edit.Append(
            ID_EDIT_ENABLE_MODULE,
            "Disable Selected Modules",
            "Disable a module to skip it when running the pipeline",
        )
        self.menu_edit_add_module = wx.Menu()
        self.menu_edit.AppendSubMenu(self.menu_edit_add_module, "&Add Module")
        self.menu_edit_goto_module = wx.Menu()
        self.menu_edit.AppendSubMenu(self.menu_edit_goto_module, "&Go to Module")

        self.menu_edit.AppendSeparator()
        self.menu_edit.Append(
            ID_EDIT_SHOW_FILE_LIST_IMAGE,
            "Show Selected Image",
            "Display the first selected image in the file list",
        )
        self.menu_edit.Append(
            ID_EDIT_REMOVE_FROM_FILE_LIST,
            "Remove From File List",
            "Remove the selected files from the file list",
        )
        self.menu_edit.Append(
            ID_EDIT_BROWSE_FOR_FILES,
            "Browse for Images",
            "Select images to add to the file list using a file browser",
        )
        self.menu_edit.Append(
            ID_EDIT_BROWSE_FOR_FOLDER,
            "Browse for Image Folder",
            "Select a folder of images to add to the file list using a file browser",
        )
        self.menu_edit.Append(
            ID_EDIT_CLEAR_FILE_LIST,
            "Clear File List",
            "Remove all files from the file list",
        )
        self.menu_edit.Append(
            ID_EDIT_EXPAND_ALL,
            "Expand All Folders",
            "Expand all folders in the file list and show all file names",
        )
        self.menu_edit.Append(
            ID_EDIT_COLLAPSE_ALL,
            "Collapse All Folders",
            "Collapse all folders in the file list, hiding all file names",
        )

        self.__menu_debug = wx.Menu()
        self.__menu_debug.Append(
            ID_DEBUG_TOGGLE, "&Start Test Mode\tF5", "Start the pipeline debugger"
        )
        self.__menu_debug.Append(
            ID_DEBUG_STEP,
            "Ste&p to Next Module\tF6",
            "Execute the currently selected module",
        )
        self.__menu_debug.Append(
            ID_DEBUG_NEXT_IMAGE_SET,
            "&Next Image Set\tF7",
            "Advance to the next image set",
        )
        self.__menu_debug.Append(
            ID_DEBUG_NEXT_GROUP,
            "Next Image &Group\tF8",
            "Advance to the next group in the image set list",
        )
        self.__menu_debug.Append(
            ID_DEBUG_CHOOSE_RANDOM_IMAGE_SET,
            "Random Image Set",
            "Advance to a random image set",
        )
        self.__menu_debug.Append(
            ID_DEBUG_CHOOSE_GROUP,
            "Choose Image Group",
            "Choose which image set group to process in test-mode",
        )
        self.__menu_debug.Append(
            ID_DEBUG_CHOOSE_IMAGE_SET,
            "Choose Image Set",
            "Choose any of the available image sets",
        )
        if not hasattr(sys, "frozen") or os.getenv("CELLPROFILER_DEBUG"):
            self.__menu_debug.Append(ID_DEBUG_RELOAD, "Reload Modules' Source")
            self.__menu_debug.Append(ID_DEBUG_PDB, "Break Into Debugger")
            #
            # Lee wants the wx debugger
            #
            if os.environ.get("USERNAME", "").lower() == "leek":
                self.__menu_debug.Append(ID_FILE_WIDGET_INSPECTOR, "Widget inspector")
        self.__menu_debug.Enable(ID_DEBUG_STEP, False)
        self.__menu_debug.Enable(ID_DEBUG_NEXT_IMAGE_SET, False)
        self.__menu_debug.Enable(ID_DEBUG_NEXT_GROUP, False)
        self.__menu_debug.Enable(ID_DEBUG_CHOOSE_GROUP, False)
        self.__menu_debug.Enable(ID_DEBUG_CHOOSE_IMAGE_SET, False)
        self.__menu_debug.Enable(ID_DEBUG_CHOOSE_RANDOM_IMAGE_SET, False)

        self.__menu_window = wx.Menu()
        self.__menu_window.Append(
            ID_WINDOW_CLOSE_ALL,
            "Close &All Open Windows\tctrl+L",
            "Close all open module display windows",
        )
        self.__menu_window.Append(
            ID_WINDOW_SHOW_ALL_WINDOWS,
            "Show All Windows On Run",
            "Show all module display windows for all modules during analysis",
        )
        self.__menu_window.Append(
            ID_WINDOW_HIDE_ALL_WINDOWS,
            "Hide All Windows On Run",
            "Hide all module display windows for all modules during analysis",
        )
        self.__menu_window.AppendSeparator()

        self.__menu_help = cellprofiler.gui.help.menu.Menu(self)

        self.__menu_bar = wx.MenuBar()
        self.__menu_bar.Append(self.__menu_file, "&File")
        self.__menu_bar.Append(self.menu_edit, "&Edit")
        self.__menu_bar.Append(self.__menu_debug, "&Test")
        if cellprofiler.preferences.get_show_sampling():
            self.__menu_sample = wx.Menu()
            self.__menu_sample.Append(
                ID_SAMPLE_INIT,
                "Initialize Sampling",
                "Initialize sampling up to current module",
            )
            self.__menu_bar.Append(self.__menu_sample, "&Sample")
        self.__menu_bar.Append(self.data_tools_menu(), "&Data Tools")
        self.__menu_bar.Append(self.__menu_window, "&Window")
        if wx.VERSION <= (2, 8, 10, 1, "") and wx.Platform == "__WXMAC__":
            self.__menu_bar.Append(self.__menu_help, "CellProfiler Help")
        else:
            self.__menu_bar.Append(self.__menu_help, "&Help")
        self.SetMenuBar(self.__menu_bar)
        self.enable_edit_commands([])

        self.Bind(wx.EVT_MENU, self.on_open_image, id=ID_FILE_OPEN_IMAGE)
        self.Bind(wx.EVT_MENU, lambda event: self.Close(), id=ID_FILE_EXIT)
        self.Bind(wx.EVT_MENU, self.__on_widget_inspector, id=ID_FILE_WIDGET_INSPECTOR)
        self.Bind(wx.EVT_MENU, self.__on_new_cp, id=ID_FILE_NEW_CP)

        self.Bind(wx.EVT_MENU, self.on_cut, id=wx.ID_CUT)
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_cut_ui, id=wx.ID_CUT)

        self.Bind(wx.EVT_MENU, self.on_copy, id=wx.ID_COPY)
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_copy_ui, id=wx.ID_COPY)

        self.Bind(wx.EVT_MENU, self.on_paste, id=wx.ID_PASTE)
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_paste_ui, id=wx.ID_PASTE)

        self.Bind(wx.EVT_MENU, self.on_select_all, id=wx.ID_SELECTALL)
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_select_all_ui, id=wx.ID_SELECTALL)

        # ID_HELP_MODULE is used in _both_ button contexts and menu contexts,
        # so it needs event bindings for either type
        self.Bind(wx.EVT_MENU, self.__on_help_module, id=ID_HELP_MODULE)
        self.Bind(wx.EVT_BUTTON, self.__on_help_module, id=ID_HELP_MODULE)

        self.Bind(wx.EVT_MENU, self.about, id=ID_HELP_ABOUT)
        self.Bind(wx.EVT_MENU, self.__on_preferences, id=ID_OPTIONS_PREFERENCES)
        self.Bind(wx.EVT_MENU, self.__on_close_all, id=ID_WINDOW_CLOSE_ALL)
        self.Bind(wx.EVT_MENU, self.__debug_pdb, id=ID_DEBUG_PDB)

        accelerator_table = wx.AcceleratorTable(
            [
                (wx.ACCEL_CMD, ord("N"), ID_FILE_ANALYZE_IMAGES),
                (wx.ACCEL_CMD, ord("O"), ID_FILE_LOAD),
                (wx.ACCEL_CMD, ord("P"), ID_FILE_SAVE_PIPELINE),
                (wx.ACCEL_CMD | wx.ACCEL_SHIFT, ord("S"), ID_FILE_SAVE),
                (wx.ACCEL_CMD, ord("L"), ID_WINDOW_CLOSE_ALL),
                (wx.ACCEL_CMD, ord("Q"), ID_FILE_EXIT),
                (wx.ACCEL_CMD, ord("W"), ID_FILE_EXIT),
                (wx.ACCEL_CMD, ord("A"), wx.ID_SELECTALL),
                (wx.ACCEL_CMD, ord("C"), wx.ID_COPY),
                (wx.ACCEL_CMD, ord("V"), wx.ID_PASTE),
                (wx.ACCEL_NORMAL, wx.WXK_F5, ID_DEBUG_TOGGLE),
                (wx.ACCEL_NORMAL, wx.WXK_F6, ID_DEBUG_STEP),
                (wx.ACCEL_NORMAL, wx.WXK_F7, ID_DEBUG_NEXT_IMAGE_SET),
                (wx.ACCEL_NORMAL, wx.WXK_F8, ID_DEBUG_NEXT_GROUP),
                (wx.ACCEL_CMD, ord("Z"), ID_EDIT_UNDO),
            ]
        )
        self.SetAcceleratorTable(accelerator_table)
        self.enable_launch_commands()