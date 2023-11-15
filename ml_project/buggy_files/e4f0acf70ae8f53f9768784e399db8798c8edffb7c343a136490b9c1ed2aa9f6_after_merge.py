    def __initiate_and_install_repositories(self, tool_shed_url, repository_revision_dict, repo_info_dicts, install_options):
        try:
            has_repository_dependencies = repository_revision_dict['has_repository_dependencies']
        except KeyError:
            raise exceptions.InternalServerError("Tool shed response missing required parameter 'has_repository_dependencies'.")
        try:
            includes_tools = repository_revision_dict['includes_tools']
        except KeyError:
            raise exceptions.InternalServerError("Tool shed response missing required parameter 'includes_tools'.")
        try:
            includes_tool_dependencies = repository_revision_dict['includes_tool_dependencies']
        except KeyError:
            raise exceptions.InternalServerError("Tool shed response missing required parameter 'includes_tool_dependencies'.")
        try:
            includes_tools_for_display_in_tool_panel = repository_revision_dict['includes_tools_for_display_in_tool_panel']
        except KeyError:
            raise exceptions.InternalServerError("Tool shed response missing required parameter 'includes_tools_for_display_in_tool_panel'.")
        # Get the information about the Galaxy components (e.g., tool panel section, tool config file, etc) that will contain the repository information.
        install_repository_dependencies = install_options.get('install_repository_dependencies', False)
        install_resolver_dependencies = install_options.get('install_resolver_dependencies', False)
        install_tool_dependencies = install_options.get('install_tool_dependencies', False)
        if install_tool_dependencies:
            self.__assert_can_install_dependencies()
        new_tool_panel_section_label = install_options.get('new_tool_panel_section_label', '')
        tool_panel_section_mapping = install_options.get('tool_panel_section_mapping', {})
        shed_tool_conf = install_options.get('shed_tool_conf', None)
        if shed_tool_conf:
            # Get the tool_path setting.
            shed_conf_dict = self.tpm.get_shed_tool_conf_dict(shed_tool_conf)
            tool_path = shed_conf_dict['tool_path']
        else:
            # Don't use migrated_tools_conf.xml and prefer shed_tool_config_file.
            try:
                for shed_config_dict in self.app.toolbox.dynamic_confs(include_migrated_tool_conf=False):
                    if shed_config_dict.get('config_filename') == self.app.config.shed_tool_config_file:
                        break
                else:
                    shed_config_dict = self.app.toolbox.dynamic_confs(include_migrated_tool_conf=False)[0]
            except IndexError:
                raise exceptions.RequestParameterMissingException("Missing required parameter 'shed_tool_conf'.")
            shed_tool_conf = shed_config_dict['config_filename']
            tool_path = shed_config_dict['tool_path']
        tool_panel_section_id = self.app.toolbox.find_section_id(install_options.get('tool_panel_section_id', ''))
        # Build the dictionary of information necessary for creating tool_shed_repository database records
        # for each repository being installed.
        installation_dict = dict(install_repository_dependencies=install_repository_dependencies,
                                 new_tool_panel_section_label=new_tool_panel_section_label,
                                 tool_panel_section_mapping=tool_panel_section_mapping,
                                 no_changes_checked=False,
                                 repo_info_dicts=repo_info_dicts,
                                 tool_panel_section_id=tool_panel_section_id,
                                 tool_path=tool_path,
                                 tool_shed_url=tool_shed_url)
        # Create the tool_shed_repository database records and gather additional information for repository installation.
        created_or_updated_tool_shed_repositories, tool_panel_section_keys, repo_info_dicts, filtered_repo_info_dicts = \
            self.handle_tool_shed_repositories(installation_dict)
        if created_or_updated_tool_shed_repositories:
            # Build the dictionary of information necessary for installing the repositories.
            installation_dict = dict(created_or_updated_tool_shed_repositories=created_or_updated_tool_shed_repositories,
                                     filtered_repo_info_dicts=filtered_repo_info_dicts,
                                     has_repository_dependencies=has_repository_dependencies,
                                     includes_tool_dependencies=includes_tool_dependencies,
                                     includes_tools=includes_tools,
                                     includes_tools_for_display_in_tool_panel=includes_tools_for_display_in_tool_panel,
                                     install_repository_dependencies=install_repository_dependencies,
                                     install_resolver_dependencies=install_resolver_dependencies,
                                     install_tool_dependencies=install_tool_dependencies,
                                     message='',
                                     new_tool_panel_section_label=new_tool_panel_section_label,
                                     shed_tool_conf=shed_tool_conf,
                                     status='done',
                                     tool_panel_section_id=tool_panel_section_id,
                                     tool_panel_section_keys=tool_panel_section_keys,
                                     tool_panel_section_mapping=tool_panel_section_mapping,
                                     tool_path=tool_path,
                                     tool_shed_url=tool_shed_url)
            # Prepare the repositories for installation.  Even though this
            # method receives a single combination of tool_shed_url, name,
            # owner and changeset_revision, there may be multiple repositories
            # for installation at this point because repository dependencies
            # may have added additional repositories for installation along
            # with the single specified repository.
            encoded_kwd, query, tool_shed_repositories, encoded_repository_ids = \
                self.initiate_repository_installation(installation_dict)
            # Some repositories may have repository dependencies that are
            # required to be installed before the dependent repository, so
            # we'll order the list of tsr_ids to ensure all repositories
            # install in the required order.
            tsr_ids = [self.app.security.encode_id(tool_shed_repository.id) for tool_shed_repository in tool_shed_repositories]

            decoded_kwd = dict(
                shed_tool_conf=shed_tool_conf,
                tool_path=tool_path,
                tool_panel_section_keys=tool_panel_section_keys,
                repo_info_dicts=filtered_repo_info_dicts,
                install_resolver_dependencies=install_resolver_dependencies,
                install_tool_dependencies=install_tool_dependencies,
                tool_panel_section_mapping=tool_panel_section_mapping,
            )
            return self.install_repositories(tsr_ids, decoded_kwd, reinstalling=False, install_options=install_options)