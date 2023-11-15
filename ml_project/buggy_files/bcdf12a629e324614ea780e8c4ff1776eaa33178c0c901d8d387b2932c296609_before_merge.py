    def feed(self, masterid, scanid):
        scan = self.lock_scan(scanid)
        if scan is None:
            raise StandardError(
                "Could not acquire lock for scan %s" % scanid
            )
        # TODO: handle "onhold" targets
        target = self.get_scan_target(scanid)
        try:
            for agentid in scan['agents']:
                if self.get_agent(agentid)['master'] == masterid:
                    for _ in range(self.may_receive(agentid)):
                        self.add_target(agentid, scanid, next(target))
        except StopIteration:
            # This scan is over, let's free its agents
            for agentid in scan['agents']:
                self.unassign_agent(agentid)
        self.update_scan_target(scanid, target)
        self.unlock_scan(scan)