    def load_file(self, path=None, env=None, silent=True, key=None):
        """Programmatically load files from ``path``.

        :param path: A single filename or a file list
        :param env: Which env to load from file (default current_env)
        :param silent: Should raise errors?
        :param key: Load a single key?
        """
        env = (env or self.current_env).upper()
        files = ensure_a_list(path)
        if files:
            already_loaded = set()
            for _filename in files:

                if py_loader.try_to_load_from_py_module_name(
                    obj=self, name=_filename, silent=True
                ):
                    # if it was possible to load from module name
                    # continue the loop.
                    continue

                filepath = os.path.join(
                    self._root_path or os.getcwd(), _filename
                )
                paths = [
                    p
                    for p in sorted(glob.glob(filepath))
                    if ".local." not in p
                ]
                local_paths = [
                    p for p in sorted(glob.glob(filepath)) if ".local." in p
                ]
                # Handle possible *.globs sorted alphanumeric
                for path in paths + local_paths:
                    if path in already_loaded:  # pragma: no cover
                        continue
                    settings_loader(
                        obj=self,
                        env=env,
                        silent=silent,
                        key=key,
                        filename=path,
                    )
                    already_loaded.add(path)