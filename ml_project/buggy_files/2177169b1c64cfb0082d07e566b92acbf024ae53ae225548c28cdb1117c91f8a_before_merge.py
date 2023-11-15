    def __init__(self, client):
        super(TaskParameters, self).__init__()

        self.state = None
        self.advertise_addr = None
        self.listen_addr = None
        self.force_new_cluster = None
        self.remote_addrs = None
        self.join_token = None

        # Spec
        self.snapshot_interval = None
        self.task_history_retention_limit = None
        self.keep_old_snapshots = None
        self.log_entries_for_slow_followers = None
        self.heartbeat_tick = None
        self.election_tick = None
        self.dispatcher_heartbeat_period = None
        self.node_cert_expiry = None
        self.external_cas = None
        self.name = None
        self.labels = None
        self.log_driver = None
        self.signing_ca_cert = None
        self.signing_ca_key = None
        self.ca_force_rotate = None
        self.autolock_managers = None
        self.rotate_worker_token = None
        self.rotate_manager_token = None

        for key, value in client.module.params.items():
            setattr(self, key, value)

        self.update_parameters(client)