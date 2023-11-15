    def deploy(self):
        '''
        Deploy salt-thin
        '''
        if self.opts.get('_caller_cachedir'):
            cachedir = self.opts.get('_caller_cachedir')
        else:
            cachedir = self.opts['cachedir']
        thin = salt.utils.thin.gen_thin(cachedir)
        self.shell.send(
            thin,
            os.path.join(self.thin_dir, 'salt-thin.tgz'),
        )
        self.deploy_ext()
        return True