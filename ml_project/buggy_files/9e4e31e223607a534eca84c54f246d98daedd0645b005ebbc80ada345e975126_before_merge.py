    def run_egg_info(self):
        assert self.source_dir
        if self.name:
            logger.debug(
                'Running setup.py (path:%s) egg_info for package %s',
                self.setup_py, self.name,
            )
        else:
            logger.debug(
                'Running setup.py (path:%s) egg_info for package from %s',
                self.setup_py, self.link,
            )

        with indent_log():
            script = self._run_setup_py
            script = script.replace('__SETUP_PY__', repr(self.setup_py))
            script = script.replace('__PKG_NAME__', repr(self.name))
            base_cmd = [sys.executable, '-c', script]
            if self.isolated:
                base_cmd += ["--no-user-cfg"]
            egg_info_cmd = base_cmd + ['egg_info']
            # We can't put the .egg-info files at the root, because then the
            # source code will be mistaken for an installed egg, causing
            # problems
            if self.editable:
                egg_base_option = []
            else:
                egg_info_dir = os.path.join(self.source_dir, 'pip-egg-info')
                ensure_dir(egg_info_dir)
                egg_base_option = ['--egg-base', 'pip-egg-info']
            cwd = self.source_dir
            if self.editable_options and \
                    'subdirectory' in self.editable_options:
                cwd = os.path.join(cwd, self.editable_options['subdirectory'])
            call_subprocess(
                egg_info_cmd + egg_base_option,
                cwd=cwd,
                show_stdout=False,
                command_level=logging.DEBUG,
                command_desc='python setup.py egg_info')

        if not self.req:
            if isinstance(
                    pkg_resources.parse_version(self.pkg_info()["Version"]),
                    Version):
                op = "=="
            else:
                op = "==="
            self.req = pkg_resources.Requirement.parse(
                "".join([
                    self.pkg_info()["Name"],
                    op,
                    self.pkg_info()["Version"],
                ]))
            self._correct_build_location()
        else:
            metadata_name = canonicalize_name(self.pkg_info()["Name"])
            if canonicalize_name(self.req.project_name) != metadata_name:
                raise InstallationError(
                    'Running setup.py (path:%s) egg_info for package %s '
                    'produced metadata for project name %s' % (
                        self.setup_py, self.name, metadata_name)
                )