    def is_docker_reachable(self):
        """
        Checks if Docker daemon is running. This is required for us to invoke the function locally

        Returns
        -------
        bool
            True, if Docker is available, False otherwise
        """
        errors = (
            docker.errors.APIError,
            requests.exceptions.ConnectionError,
        )
        if platform.system() == "Windows":
            import pywintypes  # pylint: disable=import-error

            errors += (pywintypes.error,)  # pylint: disable=no-member

        try:
            self.docker_client.ping()
            return True

        # When Docker is not installed, a request.exceptions.ConnectionError is thrown.
        # and also windows-specific errors
        except errors:
            LOG.debug("Docker is not reachable", exc_info=True)
            return False