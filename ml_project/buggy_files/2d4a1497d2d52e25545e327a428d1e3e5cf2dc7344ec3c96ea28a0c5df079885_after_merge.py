    def __init__(self, docker_client, container_id):
        """Init the class:
        docker_client: instance of Docker-py client
        container_id: Id of the container"""
        logger.debug("docker plugin - Create thread for container {}".format(container_id[:12]))
        super(ThreadDockerGrabber, self).__init__()
        # Event needed to stop properly the thread
        self._stop = threading.Event()
        # The docker-py return stats as a stream
        self._container_id = container_id
        self._stats_stream = docker_client.stats(container_id, decode=True)
        # The class return the stats as a dict
        self._stats = {}