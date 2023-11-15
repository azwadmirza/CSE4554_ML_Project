    def start_hatching(self, locust_count, hatch_rate):
        num_slaves = len(self.clients.ready) + len(self.clients.running) + len(self.clients.hatching)
        if not num_slaves:
            logger.warning("You are running in distributed mode but have no slave servers connected. "
                           "Please connect slaves prior to swarming.")
            return

        self.num_clients = locust_count
        self.hatch_rate = hatch_rate
        slave_num_clients = locust_count // (num_slaves or 1)
        slave_hatch_rate = float(hatch_rate) / (num_slaves or 1)
        remaining = locust_count % num_slaves

        logger.info("Sending hatch jobs of %d locusts and %.2f hatch rate to %d ready clients" % (slave_num_clients, slave_hatch_rate, num_slaves))

        if self.state != STATE_RUNNING and self.state != STATE_HATCHING:
            self.stats.clear_all()
            self.exceptions = {}
            events.master_start_hatching.fire()
        
        for client in (self.clients.ready + self.clients.running + self.clients.hatching):
            data = {
                "hatch_rate": slave_hatch_rate,
                "num_clients": slave_num_clients,
                "host": self.host,
                "stop_timeout": self.options.stop_timeout,
            }

            if remaining > 0:
                data["num_clients"] += 1
                remaining -= 1

            self.server.send_to_client(Message("hatch", data, client.id))
        
        self.state = STATE_HATCHING