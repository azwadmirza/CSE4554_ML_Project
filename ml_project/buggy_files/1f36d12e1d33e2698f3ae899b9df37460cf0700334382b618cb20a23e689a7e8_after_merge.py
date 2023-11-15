    def update_parameters(self, client):
        params = dict(
            snapshot_interval=self.snapshot_interval,
            task_history_retention_limit=self.task_history_retention_limit,
            keep_old_snapshots=self.keep_old_snapshots,
            log_entries_for_slow_followers=self.log_entries_for_slow_followers,
            heartbeat_tick=self.heartbeat_tick,
            election_tick=self.election_tick,
            dispatcher_heartbeat_period=self.dispatcher_heartbeat_period,
            node_cert_expiry=self.node_cert_expiry,
            name=self.name,
            signing_ca_cert=self.signing_ca_cert,
            signing_ca_key=self.signing_ca_key,
            ca_force_rotate=self.ca_force_rotate,
            autolock_managers=self.autolock_managers,
            log_driver=self.log_driver,
        )
        if self.labels:
            params['labels'] = self.labels
        self.spec = client.create_swarm_spec(**params)