    def get_worker_status(self, node_names):

        playbook = Path(DEPLOY_DIR).joinpath('ansible/worker/get_workers_status.yml')

        self.update_generate_inventory(node_names)

        loader = DataLoader()
        inventory = InventoryManager(loader=loader, sources=self.inventory_path)
        callback = AnsiblePlayBookResultsCollector(sock=self.emitter, return_results=self.output_capture, filter_output=["Print Ursula Status Data", "Print Last Log Line"])
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

        self.give_helpful_hints(node_names, playbook=playbook)