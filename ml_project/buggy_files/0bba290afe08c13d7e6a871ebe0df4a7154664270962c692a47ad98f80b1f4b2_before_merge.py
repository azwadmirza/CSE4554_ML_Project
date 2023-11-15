    def remove(self):
        if not(self.__isSwarmManager()):
            self.client.fail("This node is not a manager.")

        try:
            status_down = self.__check_node_is_down()
        except APIError:
            return

        if not(status_down):
            self.client.fail("Can not remove the node. The status node is ready and not down.")

        if not self.check_mode:
            try:
                self.client.remove_node(node_id=self.parameters.node_id, force=self.parameters.force)
            except APIError as exc:
                self.client.fail("Can not remove the node from the Swarm Cluster: %s" % to_native(exc))
        self.results['actions'].append("Node is removed from swarm cluster.")
        self.results['changed'] = True