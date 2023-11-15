    def resolve_path(path, config_file):
        """Resolve path relative to config file location.

        Args:
            path: Path to be resolved.
            config_file: Path to config file, which `path` is specified
                relative to.

        Returns:
            Path relative to the `config_file` location. If `path` is an
            absolute path then it will be returned without change.

        """
        if os.path.isabs(path):
            return path
        return os.path.relpath(path, os.path.dirname(config_file))