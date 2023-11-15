    def register_ssh_key(self, public_key):
        ssh_key = self.get_ssh_key()
        args = self._get_common_args()
        name = self.module.params.get('name')

        res = None
        if not ssh_key:
            self.result['changed'] = True
            args['publickey'] = public_key
            if not self.module.check_mode:
                args['name'] = name
                res = self.query_api('registerSSHKeyPair', **args)
        else:
            fingerprint = self._get_ssh_fingerprint(public_key)
            if ssh_key['fingerprint'] != fingerprint:
                self.result['changed'] = True
                if not self.module.check_mode:
                    # delete the ssh key with matching name but wrong fingerprint
                    args['name'] = name
                    self.query_api('deleteSSHKeyPair', **args)

            elif ssh_key['name'].lower() != name.lower():
                self.result['changed'] = True
                if not self.module.check_mode:
                    # delete the ssh key with matching fingerprint but wrong name
                    args['name'] = ssh_key['name']
                    self.query_api('deleteSSHKeyPair', **args)
                    # First match for key retrievment will be the fingerprint.
                    # We need to make another lookup if there is a key with identical name.
                    self.ssh_key = None
                    ssh_key = self.get_ssh_key()
                    if ssh_key['fingerprint'] != fingerprint:
                        args['name'] = name
                        self.query_api('deleteSSHKeyPair', **args)

            if not self.module.check_mode and self.result['changed']:
                args['publickey'] = public_key
                args['name'] = name
                res = self.query_api('registerSSHKeyPair', **args)

        if res and 'keypair' in res:
            ssh_key = res['keypair']

        return ssh_key