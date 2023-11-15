    def backup_remote_data(self, node_names):

        playbook = 'deploy/ansible/worker/backup_remote_workers.yml'
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

        self.give_helpful_hints(node_names, backup=True, playbook=playbook)