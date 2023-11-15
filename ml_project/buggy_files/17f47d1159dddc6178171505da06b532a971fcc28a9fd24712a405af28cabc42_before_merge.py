    def on_step_begin(self, **info):
        from ray.autoscaler._private.commands import kill_node
        # With 10% probability inject failure to a worker.
        if random.random() < self.probability and not self.disable:
            # With 10% probability fully terminate the node.
            should_terminate = random.random() < self.probability
            kill_node(
                self.config_path,
                yes=True,
                hard=should_terminate,
                override_cluster_name=None)