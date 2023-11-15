    def get_command_runner(self, log_prefix, node_id, auth_config,
                           cluster_name, process_runner, use_internal_ip):
        """ Returns the CommandRunner class used to perform SSH commands.

        Args:
        log_prefix(str): stores "NodeUpdater: {}: ".format(<node_id>). Used
            to print progress in the CommandRunner.
        node_id(str): the node ID.
        auth_config(dict): the authentication configs from the autoscaler
            yaml file.
        cluster_name(str): the name of the cluster.
        process_runner(module): the module to use to run the commands
            in the CommandRunner. E.g., subprocess.
        use_internal_ip(bool): whether the node_id belongs to an internal ip
            or external ip.
        """

        return SSHCommandRunner(log_prefix, node_id, self, auth_config,
                                cluster_name, process_runner, use_internal_ip)