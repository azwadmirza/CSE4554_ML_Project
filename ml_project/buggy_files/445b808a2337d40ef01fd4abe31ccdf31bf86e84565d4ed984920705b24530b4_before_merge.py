    def get_num_threads():
        """Returns the number of hardware threads."""
        lscpu_cmd = 'ssh -o StrictHostKeyChecking=no {host} {cmd}'.format(
            host=LSFUtils.get_compute_hosts()[0],
            cmd=LSFUtils._LSCPU_CMD
        )
        output = io.StringIO()
        exit_code = safe_shell_exec.execute(lscpu_cmd, stdout=output, stderr=output)
        if exit_code != 0:
            raise RuntimeError("{cmd} failed with exit code {exit_code}".format(
                cmd=lscpu_cmd, exit_code=exit_code))
        return int(yaml.safe_load(output.getvalue())[LSFUtils._THREAD_KEY])