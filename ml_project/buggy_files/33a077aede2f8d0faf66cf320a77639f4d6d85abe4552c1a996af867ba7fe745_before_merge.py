    def leave(self):
        if not(self.__isSwarmNode()):
            self.results['actions'].append("This node is not part of a swarm.")
            return
        if not self.check_mode:
            try:
                self.client.leave_swarm(force=self.parameters.force)
            except APIError as exc:
                self.client.fail("This node can not leave the Swarm Cluster: %s" % to_native(exc))
        self.results['actions'].append("Node has left the swarm cluster")
        self.results['changed'] = True