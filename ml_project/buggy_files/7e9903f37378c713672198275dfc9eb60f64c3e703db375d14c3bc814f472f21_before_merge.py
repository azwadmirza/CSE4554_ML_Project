    def terminate_nodes(self, node_ids):
        if not node_ids:
            return
        if self.cache_stopped_nodes:
            spot_ids = []
            on_demand_ids = []

            for node_id in node_ids:
                if self._get_cached_node(node_id).spot_instance_request_id:
                    spot_ids += [node_id]
                else:
                    on_demand_ids += [node_id]

            if on_demand_ids:
                # todo: show node names?
                cli_logger.print(
                    "Stopping instances {} " + cf.dimmed(
                        "(to terminate instead, "
                        "set `cache_stopped_nodes: False` "
                        "under `provider` in the cluster configuration)"),
                    cli_logger.render_list(on_demand_ids))

                self.ec2.meta.client.stop_instances(InstanceIds=on_demand_ids)
            if spot_ids:
                cli_logger.print(
                    "Terminating instances {} " +
                    cf.dimmed("(cannot stop spot instances, only terminate)"),
                    cli_logger.render_list(spot_ids))

                self.ec2.meta.client.terminate_instances(InstanceIds=spot_ids)
        else:
            self.ec2.meta.client.terminate_instances(InstanceIds=node_ids)

        for node_id in node_ids:
            self.tag_cache.pop(node_id, None)
            self.tag_cache_pending.pop(node_id, None)