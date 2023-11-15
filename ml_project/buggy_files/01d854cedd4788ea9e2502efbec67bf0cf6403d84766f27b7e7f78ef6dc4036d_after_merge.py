    def finalize_options(self):
        upload.finalize_options(self)
        if self.upload_dir is None:
            if self.has_sphinx():
                build_sphinx = self.get_finalized_command('build_sphinx')
                self.target_dir = dict(build_sphinx.builder_target_dirs)['html']
            else:
                build = self.get_finalized_command('build')
                self.target_dir = os.path.join(build.build_base, 'docs')
        else:
            self.ensure_dirname('upload_dir')
            self.target_dir = self.upload_dir
        if 'pypi.python.org' in self.repository:
            log.warn("Upload_docs command is deprecated for PyPi. Use RTD instead.")
        self.announce('Using upload directory %s' % self.target_dir)