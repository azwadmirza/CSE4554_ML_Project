    def container_remove(self, container_id, link=False, force=False):
        volume_state = (not self.parameters.keep_volumes)
        self.log("remove container container:%s v:%s link:%s force%s" % (container_id, volume_state, link, force))
        self.results['actions'].append(dict(removed=container_id, volume_state=volume_state, link=link, force=force))
        self.results['changed'] = True
        response = None
        if not self.check_mode:
            try:
                response = self.client.remove_container(container_id, v=volume_state, link=link, force=force)
            except Exception as exc:
                self.fail("Error removing container %s: %s" % (container_id, str(exc)))
        return response