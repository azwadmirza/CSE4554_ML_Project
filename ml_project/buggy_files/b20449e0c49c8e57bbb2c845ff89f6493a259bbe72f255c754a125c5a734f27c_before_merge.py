    def give_helpful_hints(self, node_names, backup=False, playbook=None):

        self.emitter.echo("some relevant info:")
        self.emitter.echo(f' config file: "{self.config_path}"')
        self.emitter.echo(f" inventory file: {self.inventory_path}", color='yellow')
        if self.config.get('keypair_path'):
            self.emitter.echo(f" keypair file: {self.config['keypair_path']}", color='yellow')

        if playbook:
            self.emitter.echo(" If you like, you can run the same playbook directly in ansible with the following:")
            self.emitter.echo(f'\tansible-playbook -i "{self.inventory_path}" "{playbook}"')

        self.emitter.echo(" You may wish to ssh into your running hosts:")
        for node_name, host_data in [h for h in self.get_all_hosts() if h[0] in node_names]:
            dep = CloudDeployers.get_deployer(host_data['provider'])(
                self.emitter,
                self.stakeholder,
                self.config['stakeholder_config_file'],
                pre_config=self.config,
                namespace=self.namespace,
                network=self.network
            )
            self.emitter.echo(f"\t{dep.format_ssh_cmd(host_data)}", color="yellow")
        if backup:
            self.emitter.echo(" *** Local backups containing sensitive data have been created. ***", color="red")
            self.emitter.echo(f" Backup data can be found here: {self.config_dir}/remote_worker_backups/")