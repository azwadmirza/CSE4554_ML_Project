    def browse(self, uri):
        logger.debug("Browsing files at: %s", uri)
        result = []
        local_path = path.uri_to_path(uri)

        if str(local_path) == "root":
            return list(self._get_media_dirs_refs())

        if not self._is_in_basedir(local_path):
            logger.warning(
                "Rejected attempt to browse path (%s) outside dirs defined "
                "in file/media_dirs config.",
                uri,
            )
            return []
        if path.uri_to_path(uri).is_file():
            logger.error("Rejected attempt to browse file (%s)", uri)
            return []

        for dir_entry in local_path.iterdir():
            child_path = dir_entry.resolve()
            uri = path.path_to_uri(child_path)

            if not self._show_dotfiles and dir_entry.name.startswith("."):
                continue

            if (
                self._excluded_file_extensions
                and dir_entry.suffix in self._excluded_file_extensions
            ):
                continue

            if child_path.is_symlink() and not self._follow_symlinks:
                logger.debug("Ignoring symlink: %s", uri)
                continue

            if not self._is_in_basedir(child_path):
                logger.debug("Ignoring symlink to outside base dir: %s", uri)
                continue

            if child_path.is_dir():
                result.append(
                    models.Ref.directory(name=dir_entry.name, uri=uri)
                )
            elif child_path.is_file():
                result.append(models.Ref.track(name=dir_entry.name, uri=uri))

        def order(item):
            return (item.type != models.Ref.DIRECTORY, item.name)

        result.sort(key=order)

        return result