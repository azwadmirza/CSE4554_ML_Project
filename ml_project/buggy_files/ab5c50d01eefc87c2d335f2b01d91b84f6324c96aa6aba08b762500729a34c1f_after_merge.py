    def install(self, install_options, global_options=[], root=None,
                prefix=None):
        if self.editable:
            self.install_editable(
                install_options, global_options, prefix=prefix)
            return
        if self.is_wheel:
            version = pip.wheel.wheel_version(self.source_dir)
            pip.wheel.check_compatibility(version, self.name)

            self.move_wheel_files(self.source_dir, root=root, prefix=prefix)
            self.install_succeeded = True
            return

        # Extend the list of global and install options passed on to
        # the setup.py call with the ones from the requirements file.
        # Options specified in requirements file override those
        # specified on the command line, since the last option given
        # to setup.py is the one that is used.
        global_options += self.options.get('global_options', [])
        install_options += self.options.get('install_options', [])

        if self.isolated:
            global_options = list(global_options) + ["--no-user-cfg"]

        temp_location = tempfile.mkdtemp('-record', 'pip-')
        record_filename = os.path.join(temp_location, 'install-record.txt')
        try:
            install_args = [sys.executable, "-u"]
            install_args.append('-c')
            install_args.append(SETUPTOOLS_SHIM % self.setup_py)
            install_args += list(global_options) + \
                ['install', '--record', record_filename]

            if not self.as_egg:
                install_args += ['--single-version-externally-managed']

            if root is not None:
                install_args += ['--root', root]
            if prefix is not None:
                install_args += ['--prefix', prefix]

            if self.pycompile:
                install_args += ["--compile"]
            else:
                install_args += ["--no-compile"]

            if running_under_virtualenv():
                py_ver_str = 'python' + sysconfig.get_python_version()
                install_args += ['--install-headers',
                                 os.path.join(sys.prefix, 'include', 'site',
                                              py_ver_str, self.name)]
            msg = 'Running setup.py install for %s' % (self.name,)
            with open_spinner(msg) as spinner:
                with indent_log():
                    call_subprocess(
                        install_args + install_options,
                        cwd=self.source_dir,
                        show_stdout=False,
                        spinner=spinner,
                    )

            if not os.path.exists(record_filename):
                logger.debug('Record file %s not found', record_filename)
                return
            self.install_succeeded = True
            if self.as_egg:
                # there's no --always-unzip option we can pass to install
                # command so we unable to save the installed-files.txt
                return

            def prepend_root(path):
                if root is None or not os.path.isabs(path):
                    return path
                else:
                    return change_root(root, path)

            with open(record_filename) as f:
                for line in f:
                    directory = os.path.dirname(line)
                    if directory.endswith('.egg-info'):
                        egg_info_dir = prepend_root(directory)
                        break
                else:
                    logger.warning(
                        'Could not find .egg-info directory in install record'
                        ' for %s',
                        self,
                    )
                    # FIXME: put the record somewhere
                    # FIXME: should this be an error?
                    return
            new_lines = []
            with open(record_filename) as f:
                for line in f:
                    filename = line.strip()
                    if os.path.isdir(filename):
                        filename += os.path.sep
                    new_lines.append(
                        os.path.relpath(
                            prepend_root(filename), egg_info_dir)
                    )
            inst_files_path = os.path.join(egg_info_dir, 'installed-files.txt')
            with open(inst_files_path, 'w') as f:
                f.write('\n'.join(new_lines) + '\n')
        finally:
            if os.path.exists(record_filename):
                os.remove(record_filename)
            rmtree(temp_location)