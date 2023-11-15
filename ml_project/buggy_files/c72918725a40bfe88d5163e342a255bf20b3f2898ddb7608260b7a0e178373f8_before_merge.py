    def update_tool_shed_repository(self, repository, tool_shed_url, latest_ctx_rev, latest_changeset_revision,
                                    install_new_dependencies=True, install_options=None):
        install_options = install_options or {}
        original_metadata_dict = repository.metadata
        original_repository_dependencies_dict = original_metadata_dict.get('repository_dependencies', {})
        original_repository_dependencies = original_repository_dependencies_dict.get('repository_dependencies', [])
        original_tool_dependencies_dict = original_metadata_dict.get('tool_dependencies', {})
        shed_tool_conf, tool_path, relative_install_dir = suc.get_tool_panel_config_tool_path_install_dir(self.app, repository)
        if tool_path:
            repo_files_dir = os.path.abspath(os.path.join(tool_path, relative_install_dir, repository.name))
        else:
            repo_files_dir = os.path.abspath(os.path.join(relative_install_dir, repository.name))
        repository_clone_url = os.path.join(tool_shed_url, 'repos', repository.owner, repository.name)
        log.info("Updating repository '%s' to %s:%s", repository.name, latest_ctx_rev, latest_changeset_revision)
        hg_util.pull_repository(repo_files_dir, repository_clone_url, latest_ctx_rev)
        hg_util.update_repository(repo_files_dir, latest_ctx_rev)
        # Remove old Data Manager entries
        if repository.includes_data_managers:
            dmh = data_manager.DataManagerHandler(self.app)
            dmh.remove_from_data_manager(repository)
        # Update the repository metadata.
        tpm = tool_panel_manager.ToolPanelManager(self.app)
        irmm = InstalledRepositoryMetadataManager(app=self.app,
                                                  tpm=tpm,
                                                  repository=repository,
                                                  changeset_revision=latest_changeset_revision,
                                                  repository_clone_url=repository_clone_url,
                                                  shed_config_dict=repository.get_shed_config_dict(self.app),
                                                  relative_install_dir=relative_install_dir,
                                                  repository_files_dir=None,
                                                  resetting_all_metadata_on_repository=False,
                                                  updating_installed_repository=True,
                                                  persist=True)
        irmm.generate_metadata_for_changeset_revision()
        irmm_metadata_dict = irmm.get_metadata_dict()
        if 'tools' in irmm_metadata_dict:
            tool_panel_dict = irmm_metadata_dict.get('tool_panel_section', None)
            if tool_panel_dict is None:
                tool_panel_dict = tpm.generate_tool_panel_dict_from_shed_tool_conf_entries(repository)
            repository_tools_tups = irmm.get_repository_tools_tups()
            tpm.add_to_tool_panel(repository_name=str(repository.name),
                                  repository_clone_url=repository_clone_url,
                                  changeset_revision=str(repository.installed_changeset_revision),
                                  repository_tools_tups=repository_tools_tups,
                                  owner=str(repository.owner),
                                  shed_tool_conf=shed_tool_conf,
                                  tool_panel_dict=tool_panel_dict,
                                  new_install=False)
            # Add new Data Manager entries
            if 'data_manager' in irmm_metadata_dict:
                dmh = data_manager.DataManagerHandler(self.app)
                dmh.install_data_managers(self.app.config.shed_data_manager_config_file,
                                          irmm_metadata_dict,
                                          repository.get_shed_config_dict(self.app),
                                          os.path.join(relative_install_dir, repository.name),
                                          repository,
                                          repository_tools_tups)
        if 'repository_dependencies' in irmm_metadata_dict or 'tool_dependencies' in irmm_metadata_dict:
            new_repository_dependencies_dict = irmm_metadata_dict.get('repository_dependencies', {})
            new_repository_dependencies = new_repository_dependencies_dict.get('repository_dependencies', [])
            new_tool_dependencies_dict = irmm_metadata_dict.get('tool_dependencies', {})
            if new_repository_dependencies:
                # [[http://localhost:9009', package_picard_1_56_0', devteam', 910b0b056666', False', False']]
                if new_repository_dependencies == original_repository_dependencies:
                    for new_repository_tup in new_repository_dependencies:
                        # Make sure all dependencies are installed.
                        # TODO: Repository dependencies that are not installed should be displayed to the user,
                        # giving them the option to install them or not. This is the same behavior as when initially
                        # installing and when re-installing.
                        new_tool_shed, new_name, new_owner, new_changeset_revision, new_pir, new_oicct = \
                            common_util.parse_repository_dependency_tuple(new_repository_tup)
                        # Mock up a repo_info_tupe that has the information needed to see if the repository dependency
                        # was previously installed.
                        repo_info_tuple = ('', new_tool_shed, new_changeset_revision, '', new_owner, [], [])
                        # Since the value of new_changeset_revision came from a repository dependency
                        # definition, it may occur earlier in the Tool Shed's repository changelog than
                        # the Galaxy tool_shed_repository.installed_changeset_revision record value, so
                        # we set from_tip to True to make sure we get the entire set of changeset revisions
                        # from the Tool Shed.
                        new_repository_db_record, installed_changeset_revision = \
                            repository_util.repository_was_previously_installed(self.app,
                                                                                tool_shed_url,
                                                                                new_name,
                                                                                repo_info_tuple,
                                                                                from_tip=True)
                        if ((new_repository_db_record and new_repository_db_record.status in [
                                self.install_model.ToolShedRepository.installation_status.ERROR,
                                self.install_model.ToolShedRepository.installation_status.NEW,
                                self.install_model.ToolShedRepository.installation_status.UNINSTALLED])
                                or not new_repository_db_record):
                            log.debug('Update to %s contains new repository dependency %s/%s', repository.name,
                                      new_owner, new_name)
                            if not install_new_dependencies:
                                return ('repository', irmm_metadata_dict)
                            else:
                                self.install(tool_shed_url, new_name, new_owner, new_changeset_revision, install_options)
            # Updates received did not include any newly defined repository dependencies but did include
            # newly defined tool dependencies.  If the newly defined tool dependencies are not the same
            # as the originally defined tool dependencies, we need to install them.
            if not install_new_dependencies:
                for new_key, new_val in new_tool_dependencies_dict.items():
                    if new_key not in original_tool_dependencies_dict:
                        return ('tool', irmm_metadata_dict)
                    original_val = original_tool_dependencies_dict[new_key]
                    if new_val != original_val:
                        return ('tool', irmm_metadata_dict)
        # Updates received did not include any newly defined repository dependencies or newly defined
        # tool dependencies that need to be installed.
        repository = self.app.update_repository_manager.update_repository_record(repository=repository,
                                                                                 updated_metadata_dict=irmm_metadata_dict,
                                                                                 updated_changeset_revision=latest_changeset_revision,
                                                                                 updated_ctx_rev=latest_ctx_rev)
        return (None, None)