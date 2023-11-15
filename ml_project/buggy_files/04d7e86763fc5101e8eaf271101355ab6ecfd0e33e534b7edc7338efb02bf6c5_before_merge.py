    def container_restart(self, container_id):
        self.results['actions'].append(dict(restarted=container_id, timeout=self.parameters.stop_timeout))
        self.results['changed'] = True
        if not self.check_mode:
            try:
                if self.parameters.stop_timeout:
                    response = self.client.restart(container_id, timeout=self.parameters.stop_timeout)
                else:
                    response = self.client.restart(container_id)
            except Exception as exc:
                self.fail("Error restarting container %s: %s" % (container_id, str(exc)))
        return self._get_container(container_id)