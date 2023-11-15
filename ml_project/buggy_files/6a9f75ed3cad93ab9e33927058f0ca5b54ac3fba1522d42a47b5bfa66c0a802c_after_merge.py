    def deploy(self):
        '''
        Deploy salt-thin
        '''
        self.shell.send(
            self.thin,
            os.path.join(self.thin_dir, 'salt-thin.tgz'),
        )
        self.deploy_ext()
        return True