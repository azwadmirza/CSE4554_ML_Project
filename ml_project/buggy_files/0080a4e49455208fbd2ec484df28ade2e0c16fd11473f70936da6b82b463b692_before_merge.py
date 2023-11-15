    def key_deploy(self, host, ret):
        '''
        Deploy the SSH key if the minions don't auth
        '''
        if not isinstance(ret[host], basestring):
            if self.opts.get('ssh_key_deploy'):
                target = self.targets[host]
                if 'passwd' in target:
                    self._key_deploy_run(host, target, False)
            return ret
        if ret[host].startswith('Permission denied'):
            target = self.targets[host]
            # permission denied, attempt to auto deploy ssh key
            print(('Permission denied for host {0}, do you want to '
                    'deploy the salt-ssh key?').format(host))
            deploy = raw_input('[Y/n]')
            if deploy.startswith(('n', 'N')):
                return ret
            target['passwd'] = getpass.getpass(
                    'Password for {0}:'.format(host)
                )
            return self._key_deploy_run(host, target, True)
        return ret