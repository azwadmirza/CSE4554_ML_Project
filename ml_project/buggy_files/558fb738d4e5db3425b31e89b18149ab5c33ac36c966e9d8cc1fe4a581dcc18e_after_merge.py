    def module_refresh(self):
        '''
        Refresh all the modules
        '''
        log.debug('Refreshing modules...')
        if self.opts['grains'].get('os') != 'MacOS':
            # In case a package has been installed into the current python
            # process 'site-packages', the 'site' module needs to be reloaded in
            # order for the newly installed package to be importable.
            try:
                reload_module(site)
            except RuntimeError:
                log.error('Error encountered during module reload. Modules were not reloaded.')
            except TypeError:
                log.error('Error encountered during module reload. Modules were not reloaded.')
        self.load_modules()
        if not self.opts.get('local', False) and self.opts.get('multiprocessing', True):
            self.functions['saltutil.refresh_modules']()