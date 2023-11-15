    def __init__(self,
                 local_dir: str,
                 remote_dir: str,
                 sync_client: Optional[SyncClient] = None):
        self.local_ip = services.get_node_ip_address()
        self.worker_ip = None

        sync_client = sync_client or DockerSyncClient()
        sync_client.configure(self._cluster_config_file)

        super(NodeSyncer, self).__init__(local_dir, remote_dir, sync_client)