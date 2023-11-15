    def update_nucypher_on_existing_nodes(self, node_names):

        playbook = 'deploy/ansible/worker/update_remote_workers.yml'

        # first update any specified input in our node config
        for k, input_specified_value in self.host_level_overrides.items():
            for node_name in node_names:
                if self.config['instances'].get(node_name):
                    # if an instance already has a specified value, we only override
                    # it if that value was input for this command invocation
                    if input_specified_value:
                        self.config['instances'][node_name][k] = input_specified_value
                    elif not self.config['instances'][node_name].get(k):
                        self.config['instances'][node_name][k] = self.config[k]
                    self._write_config()

        if self.config.get('seed_network') is True and not self.config.get('seed_node'):
            self.config['seed_node'] = list(self.config['instances'].values())[0]['publicaddress']
            self._write_config()

        self.generate_ansible_inventory(node_names)

        loader = DataLoader()
        inventory = InventoryManager(loader=loader, sources=self.inventory_path)
        callback = AnsiblePlayBookResultsCollector(sock=self.emitter, return_results=self.output_capture)
        variable_manager = VariableManager(loader=loader, inventory=inventory)

        executor = PlaybookExecutor(
            playbooks = [playbook],
            inventory=inventory,
            variable_manager=variable_manager,
            loader=loader,
            passwords=dict(),
        )
        executor._tqm._stdout_callback = callback
        executor.run()

        self.update_captured_instance_data(self.output_capture)
        self.give_helpful_hints(node_names, backup=True, playbook=playbook)