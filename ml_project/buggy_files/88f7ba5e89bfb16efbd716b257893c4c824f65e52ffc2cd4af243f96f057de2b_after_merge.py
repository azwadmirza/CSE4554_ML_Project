    def verify_env(self):
        '''
        Verify that salt-ssh is ready to run
        '''
        if not salt.utils.which('sshpass'):
            log.warning('Warning:  sshpass is not present, so password-based '
                        'authentication is not available.')