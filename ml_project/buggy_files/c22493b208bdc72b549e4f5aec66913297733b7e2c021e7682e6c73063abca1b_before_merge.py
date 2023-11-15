    def __init__(self, opts):
        # Late setup of the opts grains, so we can log from the grains module
        import salt.loader
        opts['grains'] = salt.loader.grains(opts)
        super(SMinion, self).__init__(opts)

        # Clean out the proc directory (default /var/cache/salt/minion/proc)
        if (self.opts.get('file_client', 'remote') == 'remote'
                or self.opts.get('use_master_when_local', False)):
            install_zmq()
            io_loop = ZMQDefaultLoop.current()
            io_loop.run_sync(
                lambda: self.eval_master(self.opts, failed=True)
            )
        self.gen_modules(initial_load=True)

        # If configured, cache pillar data on the minion
        if self.opts['file_client'] == 'remote' and self.opts.get('minion_pillar_cache', False):
            import salt.utils.yaml
            pdir = os.path.join(self.opts['cachedir'], 'pillar')
            if not os.path.isdir(pdir):
                os.makedirs(pdir, 0o700)
            ptop = os.path.join(pdir, 'top.sls')
            if self.opts['saltenv'] is not None:
                penv = self.opts['saltenv']
            else:
                penv = 'base'
            cache_top = {penv: {self.opts['id']: ['cache']}}
            with salt.utils.files.fopen(ptop, 'wb') as fp_:
                salt.utils.yaml.safe_dump(cache_top, fp_)
                os.chmod(ptop, 0o600)
            cache_sls = os.path.join(pdir, 'cache.sls')
            with salt.utils.files.fopen(cache_sls, 'wb') as fp_:
                salt.utils.yaml.safe_dump(self.opts['pillar'], fp_)
                os.chmod(cache_sls, 0o600)