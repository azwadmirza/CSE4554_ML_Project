    def restore_from_backup(self, target_host, source_path):

        playbook = 'deploy/ansible/worker/restore_ursula_from_backup.yml'

        self.generate_ansible_inventory([target_host], restore_path=source_path)

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
        self.give_helpful_hints([target_host], backup=True, playbook=playbook)