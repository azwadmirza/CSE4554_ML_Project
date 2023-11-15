    def _create_keypair(self):
        new_keypair_data = self.ec2Client.create_key_pair(KeyName=f'{self.namespace_network}')
        outpath = os.path.join(DEFAULT_CONFIG_ROOT, NODE_CONFIG_STORAGE_KEY, f'{self.namespace_network}.awskeypair')
        os.makedirs(os.path.dirname(outpath), exist_ok=True)
        with open(outpath, 'w') as outfile:
            outfile.write(new_keypair_data['KeyMaterial'])
        # set local keypair permissions https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html
        os.chmod(outpath, 0o400)
        self.emitter.echo(f"a new aws keypair was saved to {outpath}, keep it safe.", color='yellow')
        return new_keypair_data['KeyName'], outpath