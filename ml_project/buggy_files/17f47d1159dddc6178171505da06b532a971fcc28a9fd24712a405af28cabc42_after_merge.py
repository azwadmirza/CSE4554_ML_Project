    def on_step_begin(self, **info):
        import click
        from ray.autoscaler._private.commands import kill_node
        failures = 0
        max_failures = 3
        # With 10% probability inject failure to a worker.
        if random.random() < self.probability and not self.disable:
            # With 10% probability fully terminate the node.
            should_terminate = random.random() < self.probability
            while failures < max_failures:
                try:
                    kill_node(
                        self.config_path,
                        yes=True,
                        hard=should_terminate,
                        override_cluster_name=None)
                except click.exceptions.ClickException:
                    failures += 1
                    logger.exception("Killing random node failed in attempt "
                                     "{}. "
                                     "Retrying {} more times".format(
                                         str(failures),
                                         str(max_failures - failures)))