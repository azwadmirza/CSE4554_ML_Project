    def set_repository(self, repository, relative_install_dir=None, changeset_revision=None):
        self.repository = repository
        # Shed related tool panel configs are only relevant to Galaxy.
        if self.app.name == 'galaxy':
            if relative_install_dir is None and self.repository is not None:
                tool_path, relative_install_dir = self.repository.get_tool_relative_path(self.app)
            if changeset_revision is None and self.repository is not None:
                self.set_changeset_revision(self.repository.changeset_revision)
            else:
                self.set_changeset_revision(changeset_revision)
            self.shed_config_dict = repository.get_shed_config_dict(self.app, {})
            self.metadata_dict = {'shed_config_filename': self.shed_config_dict.get('config_filename', None)}
        else:
            if relative_install_dir is None and self.repository is not None:
                relative_install_dir = repository.repo_path(self.app)
            if changeset_revision is None and self.repository is not None:
                self.set_changeset_revision(self.repository.tip(self.app))
            else:
                self.set_changeset_revision(changeset_revision)
            self.shed_config_dict = {}
            self.metadata_dict = {}
        self.set_relative_install_dir(relative_install_dir)
        self.set_repository_files_dir()
        self.resetting_all_metadata_on_repository = False
        self.updating_installed_repository = False
        self.persist = False
        self.invalid_file_tups = []