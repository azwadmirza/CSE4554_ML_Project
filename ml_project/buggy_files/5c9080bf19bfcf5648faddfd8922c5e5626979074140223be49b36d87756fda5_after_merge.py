    def get_exit_codes(self, output):
        """Get exit code for all hosts in output *if available*.
        Output parameter is modified in-place.

        :param output: As returned by
          :py:func:`pssh.pssh_client.ParallelSSHClient.get_output`
        :rtype: None
        """
        if isinstance(output, list):
            for host_out in output:
                if host_out is None:
                    continue
            host_out.exit_code = self.get_exit_code(host_out)
        elif isinstance(output, dict):
            for host in output:
                host_out = output[host]
                if output[host] is None:
                    continue
                host_out.exit_code = self.get_exit_code(host_out)
        else:
            raise ValueError("Unexpected output object type")