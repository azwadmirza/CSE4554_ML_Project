    def _compose(self, detached=False):
        """
        Args:
            detached:
        """
        compose_cmd = "docker-compose"

        command = [
            compose_cmd,
            "-f",
            os.path.join(self.container_root, DOCKER_COMPOSE_FILENAME),
            "up",
            "--build",
            "--abort-on-container-exit",
        ]

        if detached:
            command.append("-d")

        logger.info("docker command: %s", " ".join(command))
        return command