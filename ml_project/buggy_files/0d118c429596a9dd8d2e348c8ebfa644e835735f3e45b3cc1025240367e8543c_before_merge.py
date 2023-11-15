    def install_editable(self, install_options,
                         global_options=(), prefix=None):
        logger.info('Running setup.py develop for %s', self.name)

        if self.isolated:
            global_options = list(global_options) + ["--no-user-cfg"]

        if prefix:
            prefix_param = ['--prefix={0}'.format(prefix)]
            install_options = list(install_options) + prefix_param

        with indent_log():
            # FIXME: should we do --install-headers here too?
            cwd = self.source_dir
            if self.editable_options and \
                    'subdirectory' in self.editable_options:
                cwd = os.path.join(cwd, self.editable_options['subdirectory'])
            call_subprocess(
                [
                    sys.executable,
                    '-c',
                    "import setuptools, tokenize; __file__=%r; exec(compile("
                    "getattr(tokenize, 'open', open)(__file__).read().replace"
                    "('\\r\\n', '\\n'), __file__, 'exec'))" % self.setup_py
                ] +
                list(global_options) +
                ['develop', '--no-deps'] +
                list(install_options),

                cwd=cwd,
                show_stdout=False)

        self.install_succeeded = True