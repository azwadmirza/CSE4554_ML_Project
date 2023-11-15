    def install(self, tool_shed_url, name, owner, changeset_revision, install_options):
        # Get all of the information necessary for installing the repository from the specified tool shed.
        repository_revision_dict, repo_info_dicts = self.__get_install_info_from_tool_shed(tool_shed_url,
                                                                                           name,
                                                                                           owner,
                                                                                           changeset_revision)
        if changeset_revision != repository_revision_dict['changeset_revision']:
            # Demanded installation of a non-installable revision. Stop here if repository already installed.
            repo = repository_util.get_installed_repository(
                app=self.app,
                tool_shed=tool_shed_url,
                name=name,
                owner=owner,
                changeset_revision=repository_revision_dict['changeset_revision'],
            )
            if repo and repo.is_installed:
                # Repo installed. Returning empty list indicated repo already installed.
                return []
        installed_tool_shed_repositories = self.__initiate_and_install_repositories(
            tool_shed_url,
            repository_revision_dict,
            repo_info_dicts,
            install_options
        )
        return installed_tool_shed_repositories