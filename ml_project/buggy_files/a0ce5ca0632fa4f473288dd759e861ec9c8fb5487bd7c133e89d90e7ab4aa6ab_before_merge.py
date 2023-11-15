    def _check_if_in_local_vm(self, runner: Runner) -> bool:
        # Minikube just has 'minikube' as context'
        if self.context == "minikube":
            return True
        # Minishift has complex context name, so check by server:
        if self.command == "oc":
            try:
                ip = runner.get_output(["minishift", "ip"]).strip()
            except (OSError, CalledProcessError):
                return False
            if ip and ip in self.server:
                return True
        return False