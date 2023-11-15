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

        self.tag_cache.pop(node_id, None)
        self.tag_cache_pending.pop(node_id, None)