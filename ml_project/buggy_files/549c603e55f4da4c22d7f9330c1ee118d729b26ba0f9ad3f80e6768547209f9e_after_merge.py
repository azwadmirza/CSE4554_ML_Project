    def finalize_options(self):
        install.finalize_options(self)
        for optname in ('root_dir', 'config_dir', 'cache_dir', 'sock_dir',
                        'srv_root_dir', 'base_file_roots_dir',
                        'base_pillar_roots_dir', 'base_master_roots_dir',
                        'logs_dir', 'pidfile_dir'):
            optvalue = getattr(self, 'salt_{0}'.format(optname))
            if not optvalue:
                raise RuntimeError(
                    'The value of --salt-{0} needs a proper path value'.format(
                        optname.replace('_', '-')
                    )
                )
            setattr(self.distribution, 'salt_{0}'.format(optname), optvalue)