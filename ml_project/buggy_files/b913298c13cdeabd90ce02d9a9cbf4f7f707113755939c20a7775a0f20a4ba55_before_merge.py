    def _home(self):
        # TODO (Dmitri): Think about how to use the node's HOME variable
        # without making an extra kubectl exec call.
        if self._home_cached is None:
            cmd = self.kubectl + [
                "exec", "-it", self.node_id, "--", "printenv", "HOME"
            ]
            joined_cmd = " ".join(cmd)
            raw_out = self.process_runner.check_output(joined_cmd, shell=True)
            self._home_cached = raw_out.decode().strip("\n\r")
        return self._home_cached