    def finalize_options(self):
        install.finalize_options(self)
        for optname in ('root_dir', 'config_dir', 'cache_dir', 'sock_dir',
                        'base_file_roots_dir', 'base_pillar_roots_dir',
                        'base_master_roots_dir', 'logs_dir', 'pidfile_dir'):
            if not getattr(self, 'salt_{0}'.format(optname)):
                raise RuntimeError(
                    'The value of --salt-{0} needs a proper path value'.format(
                        optname.replace('_', '-')
                    )
                )