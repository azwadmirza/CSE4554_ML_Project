    def get_docker_network(self, container_id, all_stats):
        """Return the container network usage using the Docker API (v1.0 or higher).

        Input: id is the full container id
        Output: a dict {'time_since_update': 3000, 'rx': 10, 'tx': 65}.
        with:
            time_since_update: number of seconds elapsed between the latest grab
            rx: Number of byte received
            tx: Number of byte transmited
        """
        # Init the returned dict
        network_new = {}

        # Read the rx/tx stats (in bytes)
        try:
            netcounters = all_stats["network"]
        except KeyError as e:
            # all_stats do not have NETWORK information
            logger.debug("Can not grab NET usage for container {0} ({1})".format(container_id, e))
            # No fallback available...
            return network_new

        # Previous network interface stats are stored in the network_old variable
        if not hasattr(self, 'inetcounters_old'):
            # First call, we init the network_old var
            self.netcounters_old = {}
            try:
                self.netcounters_old[container_id] = netcounters
            except (IOError, UnboundLocalError):
                pass

        if container_id not in self.netcounters_old:
            try:
                self.netcounters_old[container_id] = netcounters
            except (IOError, UnboundLocalError):
                pass
        else:
            # By storing time data we enable Rx/s and Tx/s calculations in the
            # XML/RPC API, which would otherwise be overly difficult work
            # for users of the API
            network_new['time_since_update'] = getTimeSinceLastUpdate('docker_net_{0}'.format(container_id))
            network_new['rx'] = netcounters["rx_bytes"] - self.netcounters_old[container_id]["rx_bytes"]
            network_new['tx'] = netcounters["tx_bytes"] - self.netcounters_old[container_id]["tx_bytes"]
            network_new['cumulative_rx'] = netcounters["rx_bytes"]
            network_new['cumulative_tx'] = netcounters["tx_bytes"]

            # Save stats to compute next bitrate
            self.netcounters_old[container_id] = netcounters

        # Return the stats
        return network_new