    def get_command_runner(self,
                           log_prefix,
                           node_id,
                           auth_config,
                           cluster_name,
                           process_runner,
                           use_internal_ip,
                           docker_config=None):
        return KubernetesCommandRunner(log_prefix, self.namespace, node_id,
                                       auth_config, process_runner)