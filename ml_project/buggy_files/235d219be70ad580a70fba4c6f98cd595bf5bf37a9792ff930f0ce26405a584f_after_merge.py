    def install_tool_shed_repository(self, tool_shed_repository, repo_info_dict, tool_panel_section_key, shed_tool_conf, tool_path,
                                     install_resolver_dependencies, install_tool_dependencies, reinstalling=False,
                                     tool_panel_section_mapping={}, install_options=None):
        self.app.install_model.context.flush()
        if tool_panel_section_key:
            _, tool_section = self.app.toolbox.get_section(tool_panel_section_key)
            if tool_section is None:
                log.debug('Invalid tool_panel_section_key "%s" specified.  Tools will be loaded outside of sections in the tool panel.',
                          str(tool_panel_section_key))
        else:
            tool_section = None
        if isinstance(repo_info_dict, string_types):
            repo_info_dict = encoding_util.tool_shed_decode(repo_info_dict)
        repo_info_tuple = repo_info_dict[tool_shed_repository.name]
        description, repository_clone_url, changeset_revision, ctx_rev, repository_owner, repository_dependencies, tool_dependencies = repo_info_tuple
        if changeset_revision != tool_shed_repository.changeset_revision:
            # This is an update
            tool_shed_url = common_util.get_tool_shed_url_from_tool_shed_registry(self.app, tool_shed_repository.tool_shed)
            return self.update_tool_shed_repository(tool_shed_repository,
                                                    tool_shed_url,
                                                    ctx_rev,
                                                    changeset_revision,
                                                    install_options=install_options)
        # Clone the repository to the configured location.
        self.update_tool_shed_repository_status(tool_shed_repository,
                                                self.install_model.ToolShedRepository.installation_status.CLONING)
        relative_clone_dir = repository_util.generate_tool_shed_repository_install_dir(repository_clone_url,
                                                                                       tool_shed_repository.installed_changeset_revision)
        relative_install_dir = os.path.join(relative_clone_dir, tool_shed_repository.name)
        install_dir = os.path.abspath(os.path.join(tool_path, relative_install_dir))
        log.info("Cloning repository '%s' at %s:%s", repository_clone_url, ctx_rev, tool_shed_repository.changeset_revision)
        if os.path.exists(install_dir):
            # May exist from a previous failed install attempt, just try updating instead of cloning.
            hg_util.pull_repository(install_dir, repository_clone_url, ctx_rev)
            hg_util.update_repository(install_dir, ctx_rev)
            cloned_ok = True
        else:
            cloned_ok, error_message = hg_util.clone_repository(repository_clone_url, install_dir, ctx_rev)
        if cloned_ok:
            if reinstalling:
                # Since we're reinstalling the repository we need to find the latest changeset revision to
                # which it can be updated.
                changeset_revision_dict = self.app.update_repository_manager.get_update_to_changeset_revision_and_ctx_rev(tool_shed_repository)
                current_changeset_revision = changeset_revision_dict.get('changeset_revision', None)
                current_ctx_rev = changeset_revision_dict.get('ctx_rev', None)
                if current_ctx_rev != ctx_rev:
                    repo_path = os.path.abspath(install_dir)
                    hg_util.pull_repository(repo_path, repository_clone_url, current_changeset_revision)
                    hg_util.update_repository(repo_path, ctx_rev=current_ctx_rev)
            self.__handle_repository_contents(tool_shed_repository=tool_shed_repository,
                                              tool_path=tool_path,
                                              repository_clone_url=repository_clone_url,
                                              relative_install_dir=relative_install_dir,
                                              tool_shed=tool_shed_repository.tool_shed,
                                              tool_section=tool_section,
                                              shed_tool_conf=shed_tool_conf,
                                              reinstalling=reinstalling,
                                              tool_panel_section_mapping=tool_panel_section_mapping)
            metadata = tool_shed_repository.metadata
            if 'tools' in metadata and install_resolver_dependencies:
                self.update_tool_shed_repository_status(tool_shed_repository,
                                                        self.install_model.ToolShedRepository.installation_status.INSTALLING_TOOL_DEPENDENCIES)
                new_tools = [self.app.toolbox._tools_by_id.get(tool_d['guid'], None) for tool_d in metadata['tools']]
                new_requirements = set([tool.requirements.packages for tool in new_tools if tool])
                [self._view.install_dependencies(r) for r in new_requirements]
                dependency_manager = self.app.toolbox.dependency_manager
                if dependency_manager.cached:
                    [dependency_manager.build_cache(r) for r in new_requirements]

            if install_tool_dependencies and tool_shed_repository.tool_dependencies and 'tool_dependencies' in metadata:
                work_dir = tempfile.mkdtemp(prefix="tmp-toolshed-itsr")
                # Install tool dependencies.
                self.update_tool_shed_repository_status(tool_shed_repository,
                                                        self.install_model.ToolShedRepository.installation_status.INSTALLING_TOOL_DEPENDENCIES)
                # Get the tool_dependencies.xml file from the repository.
                tool_dependencies_config = hg_util.get_config_from_disk('tool_dependencies.xml', install_dir)
                itdm = InstallToolDependencyManager(self.app)
                itdm.install_specified_tool_dependencies(tool_shed_repository=tool_shed_repository,
                                                         tool_dependencies_config=tool_dependencies_config,
                                                         tool_dependencies=tool_shed_repository.tool_dependencies,
                                                         from_tool_migration_manager=False)
                basic_util.remove_dir(work_dir)
            self.update_tool_shed_repository_status(tool_shed_repository,
                                                    self.install_model.ToolShedRepository.installation_status.INSTALLED)
            if self.app.config.manage_dependency_relationships:
                # Add the installed repository and any tool dependencies to the in-memory dictionaries
                # in the installed_repository_manager.
                self.app.installed_repository_manager.handle_repository_install(tool_shed_repository)
        else:
            # An error occurred while cloning the repository, so reset everything necessary to enable another attempt.
            repository_util.set_repository_attributes(self.app,
                                                      tool_shed_repository,
                                                      status=self.install_model.ToolShedRepository.installation_status.ERROR,
                                                      error_message=error_message,
                                                      deleted=False,
                                                      uninstalled=False,
                                                      remove_from_disk=True)