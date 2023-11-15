    def create_file_manage_actions(self, fnames):
        """Return file management actions"""
        only_files = all([osp.isfile(_fn) for _fn in fnames])
        only_modules = all([osp.splitext(_fn)[1] in ('.py', '.pyw', '.ipy')
                            for _fn in fnames])
        only_notebooks = all([osp.splitext(_fn)[1] == '.ipynb'
                              for _fn in fnames])
        only_valid = all([encoding.is_text_file(_fn) for _fn in fnames])
        run_action = create_action(self, _("Run"), icon=ima.icon('run'),
                                   triggered=self.run)
        edit_action = create_action(self, _("Edit"), icon=ima.icon('edit'),
                                    triggered=self.clicked)
        move_action = create_action(self, _("Move..."),
                                    icon="move.png",
                                    triggered=self.move)
        delete_action = create_action(self, _("Delete..."),
                                      icon=ima.icon('editdelete'),
                                      triggered=self.delete)
        rename_action = create_action(self, _("Rename..."),
                                      icon=ima.icon('rename'),
                                      triggered=self.rename)
        open_external_action = create_action(self, _("Open With OS"), 
                                             triggered=self.open_external)
        ipynb_convert_action = create_action(self, _("Convert to Python script"),
                                             icon=ima.icon('python'),
                                             triggered=self.convert_notebooks)
        
        actions = []
        if only_modules:
            actions.append(run_action)
        if only_valid and only_files:
            actions.append(edit_action)
        
        if sys.platform == 'darwin':
            text=_("Show in Finder")
        else:
            text=_("Show in Folder")
        external_fileexp_action = create_action(self, text, 
                                triggered=self.show_in_external_file_explorer)        
        actions += [delete_action, rename_action]
        basedir = fixpath(osp.dirname(fnames[0]))
        if all([fixpath(osp.dirname(_fn)) == basedir for _fn in fnames]):
            actions.append(move_action)
        actions += [None]
        if only_files:
            actions.append(open_external_action)
        actions.append(external_fileexp_action)
        actions.append([None])
        if only_notebooks and nbexporter is not None:
            actions.append(ipynb_convert_action)

        # VCS support is quite limited for now, so we are enabling the VCS
        # related actions only when a single file/folder is selected:
        dirname = fnames[0] if osp.isdir(fnames[0]) else osp.dirname(fnames[0])
        if len(fnames) == 1 and vcs.is_vcs_repository(dirname):
            # QAction.triggered works differently for PySide and PyQt
            commit_slot = lambda fnames=[dirname]:\
                                self.vcs_command(fnames, 'commit')
            browse_slot = lambda fnames=[dirname]:\
                                self.vcs_command(fnames, 'browse')
            vcs_ci = create_action(self, _("Commit"),
                                   icon=ima.icon('vcs_commit'),
                                   triggered=commit_slot)
            vcs_log = create_action(self, _("Browse repository"),
                                    icon=ima.icon('vcs_browse'),
                                    triggered=browse_slot)
            actions += [None, vcs_ci, vcs_log]

        return actions