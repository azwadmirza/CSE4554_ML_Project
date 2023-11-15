    def install(self, tool_shed_url, name, owner, changeset_revision, install_options):
        # Get all of the information necessary for installing the repository from the specified tool shed.
        repository_revision_dict, repo_info_dicts = self.__get_install_info_from_tool_shed(tool_shed_url,
                                                                                           name,
                                                                                           owner,
                                                                                           changeset_revision)
        installed_tool_shed_repositories = self.__initiate_and_install_repositories(
            tool_shed_url,
            repository_revision_dict,
            repo_info_dicts,
            install_options
        )
        return installed_tool_shed_repositories