    def setup_open_files(self):
        """Open the list of saved files per project"""
        self.set_create_new_file_if_empty(False)
        active_project_path = None
        if self.projects is not None:
            active_project_path = self.projects.get_active_project_path()

        if active_project_path:
            filenames = self.projects.get_project_filenames()
        else:
            filenames = self.get_option('filenames', default=[])
        self.close_all_files()

        if filenames and any([osp.isfile(f) for f in filenames]):
            layout = self.get_option('layout_settings', None)
            # Check if no saved layout settings exist, e.g. clean prefs file
            # If not, load with default focus/layout, to fix issue #8458 .
            if layout:
                is_vertical, cfname, clines = layout.get('splitsettings')[0]
                if cfname in filenames:
                    index = filenames.index(cfname)
                    # First we load the last focused file.
                    self.load(filenames[index], goto=clines[index],
                              set_focus=True)
                    # Then we load the files located to the left of the last
                    # focused file in the tabbar, while keeping the focus on
                    # the last focused file.
                    if index > 0:
                        self.load(filenames[index::-1], goto=clines[index::-1],
                                  set_focus=False, add_where='start')
                    # Finally we load the files to the right of the last
                    # focused file in the tabbar, while keeping the focus on
                    # the last focused file.
                    if index < (len(filenames) - 1):
                        self.load(filenames[index+1:], goto=clines[index:],
                                  set_focus=False, add_where='end')
                else:
                    self.load(filenames, goto=clines)
            else:
                self.load(filenames)

            if self.__first_open_files_setup:
                self.__first_open_files_setup = False
                if layout is not None:
                    self.editorsplitter.set_layout_settings(
                        layout,
                        dont_goto=filenames[0])
                win_layout = self.get_option('windows_layout_settings', [])
                if win_layout:
                    for layout_settings in win_layout:
                        self.editorwindows_to_be_created.append(
                            layout_settings)
                self.set_last_focus_editorstack(self, self.editorstacks[0])
        else:
            self.__load_temp_file()
        self.set_create_new_file_if_empty(True)