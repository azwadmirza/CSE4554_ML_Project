    def _delete_keypair(self):
        # only use self.namespace here to avoid accidental deletions of pre-existing keypairs
        deleted_keypair_data = self.ec2Client.delete_key_pair(KeyName=f'{self.namespace_network}')
        if deleted_keypair_data['HTTPStatusCode'] == 200:
            outpath = Path(DEFAULT_CONFIG_ROOT).joinpath(NODE_CONFIG_STORAGE_KEY, f'{self.namespace_network}.awskeypair')
            os.remove(outpath)
            self.emitter.echo(f"keypair at {outpath}, was deleted", color='yellow')