    def terminate_node(self, node_id):
        node = self._get_cached_node(node_id)
        if self.cache_stopped_nodes:
            if node.spot_instance_request_id:
                cli_logger.print(
                    "Terminating instance {} " +
                    cf.dimmed("(cannot stop spot instances, only terminate)"),
                    node_id)  # todo: show node name?
                node.terminate()
            else:
                cli_logger.print("Stopping instance {} " + cf.dimmed(
                    "(to terminate instead, "
                    "set `cache_stopped_nodes: False` "
                    "under `provider` in the cluster configuration)"),
                                 node_id)  # todo: show node name?
                node.stop()
        else:
            node.terminate()

        # TODO (Alex): We are leaking the tag cache here. Naively, we would
        # want to just remove the cache entry here, but terminating can be
        # asyncrhonous or error, which would result in a use after free error.
        # If this leak becomes bad, we can garbage collect the tag cache when
        # the node cache is updated.
        pass