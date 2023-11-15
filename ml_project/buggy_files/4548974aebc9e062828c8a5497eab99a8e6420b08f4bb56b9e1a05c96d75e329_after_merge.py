    def _read_git_repository(self, path: Path) -> None:
        """Process a custom repository folder."""
        slug = extract_hash_from_path(path)

        # exists repository json
        try:
            repository_file = find_one_filetype(
                path, "repository", FILE_SUFFIX_CONFIGURATION
            )
        except ConfigurationFileError:
            _LOGGER.warning("No repository information exists at %s", path)
            return

        try:
            repository_info = SCHEMA_REPOSITORY_CONFIG(
                read_json_or_yaml_file(repository_file)
            )
        except ConfigurationFileError:
            _LOGGER.warning(
                "Can't read repository information from %s", repository_file
            )
            return
        except vol.Invalid:
            _LOGGER.warning("Repository parse error %s", repository_file)
            return

        # process data
        self.repositories[slug] = repository_info
        self._read_addons_folder(path, slug)