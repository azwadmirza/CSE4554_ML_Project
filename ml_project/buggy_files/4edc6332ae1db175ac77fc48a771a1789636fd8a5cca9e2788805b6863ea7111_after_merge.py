    def __init__(self, deployment_name, pod_name, deployment_config):
        self.deployment_name = deployment_name
        self.pod_name = pod_name
        self.deployment_config = deployment_config
        cs = deployment_config["spec"]["template"]["spec"]["containers"]
        self.container_config = [
            c for c in cs if "telepresence-k8s" in c["image"]
        ][0]
        self.container_name = self.container_config["name"]
        # Wait for pod to be running before we can get environment:
        wait_for_pod(self)
        self.pod_environment = _get_remote_env(pod_name, self.container_name)
        self.service_names = _get_service_names(self.pod_environment)