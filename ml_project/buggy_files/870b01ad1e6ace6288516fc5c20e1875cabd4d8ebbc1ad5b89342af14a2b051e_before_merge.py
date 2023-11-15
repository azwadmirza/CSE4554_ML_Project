    def __init__(self, opts):
        # Late setup of the opts grains, so we can log from the grains module
        opts['grains'] = salt.loader.grains(opts)
        super(SMinion, self).__init__(opts)

        # Clean out the proc directory (default /var/cache/salt/minion/proc)
        if (self.opts.get('file_client', 'remote') == 'remote'
                or self.opts.get('use_master_when_local', False)):
            self.eval_master(self.opts, failed=True)
        self.gen_modules(initial_load=True)