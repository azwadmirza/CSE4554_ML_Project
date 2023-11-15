    def join(self):
        if self.__isSwarmNode():
            self.results['actions'].append("This node is already part of a swarm.")
            return
        if not self.check_mode:
            try:
                self.client.join_swarm(
                    remote_addrs=self.parameters.remote_addrs, join_token=self.parameters.join_token, listen_addr=self.parameters.listen_addr,
                    advertise_addr=self.parameters.advertise_addr)
            except APIError as exc:
                self.client.fail("Can not join the Swarm Cluster: %s" % to_native(exc))
        self.results['actions'].append("New node is added to swarm cluster")
        self.results['changed'] = True