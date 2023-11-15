    def spawn_updater(self, node_id, init_commands, ray_start_commands):
        updater = NodeUpdaterThread(
            node_id=node_id,
            provider_config=self.config["provider"],
            provider=self.provider,
            auth_config=self.config["auth"],
            cluster_name=self.config["cluster_name"],
            file_mounts=self.config["file_mounts"],
            initialization_commands=with_head_node_ip(
                self.config["initialization_commands"]),
            setup_commands=with_head_node_ip(init_commands),
            ray_start_commands=with_head_node_ip(ray_start_commands),
            runtime_hash=self.runtime_hash,
            process_runner=self.process_runner,
            use_internal_ip=True)
        updater.start()
        self.updaters[node_id] = updater