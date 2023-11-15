    def __update_swarm(self):
        try:
            self.inspect_swarm()
            version = self.swarm_info['Version']['Index']
            spec = self.swarm_info['Spec']
            new_spec = self.__update_spec(spec)
            del spec['TaskDefaults']
            if spec == new_spec:
                self.results['actions'].append("No modification")
                self.results['changed'] = False
                return
            if not self.check_mode:
                self.client.update_swarm(
                    version=version, swarm_spec=new_spec, rotate_worker_token=self.parameters.rotate_worker_token,
                    rotate_manager_token=self.parameters.rotate_manager_token)
        except APIError as exc:
            self.client.fail("Can not update a Swarm Cluster: %s" % to_native(exc))
            return

        self.inspect_swarm()
        self.results['actions'].append("Swarm cluster updated")
        self.results['changed'] = True