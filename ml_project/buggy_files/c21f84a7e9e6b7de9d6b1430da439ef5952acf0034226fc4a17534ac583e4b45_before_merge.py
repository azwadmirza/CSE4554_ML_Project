    def fetch_build_egg(self, req):
        """Fetch an egg needed for building"""
        from pex.third_party.setuptools.command.easy_install import easy_install
        dist = self.__class__({'script_args': ['easy_install']})
        opts = dist.get_option_dict('easy_install')
        opts.clear()
        opts.update(
            (k, v)
            for k, v in self.get_option_dict('easy_install').items()
            if k in (
                # don't use any other settings
                'find_links', 'site_dirs', 'index_url',
                'optimize', 'site_dirs', 'allow_hosts',
            ))
        if self.dependency_links:
            links = self.dependency_links[:]
            if 'find_links' in opts:
                links = opts['find_links'][1] + links
            opts['find_links'] = ('setup', links)
        install_dir = self.get_egg_cache_dir()
        cmd = easy_install(
            dist, args=["x"], install_dir=install_dir,
            exclude_scripts=True,
            always_copy=False, build_directory=None, editable=False,
            upgrade=False, multi_version=True, no_report=True, user=False
        )
        cmd.ensure_finalized()
        return cmd.easy_install(req)