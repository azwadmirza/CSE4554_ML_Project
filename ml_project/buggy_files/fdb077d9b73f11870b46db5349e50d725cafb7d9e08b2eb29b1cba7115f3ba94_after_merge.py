    def is_failover_possible(self, cluster, leader, candidate):
        if leader and (not cluster.leader or cluster.leader.name != leader):
            return 'leader name does not match'
        if candidate:
            members = [m for m in cluster.members if m.name == candidate]
            if not members:
                return 'candidate does not exists'
        else:
            members = [m for m in cluster.members if m.name != cluster.leader.name and m.api_url]
            if not members:
                return 'failover is not possible: cluster does not have members except leader'
        for st in self.server.patroni.ha.fetch_nodes_statuses(members):
            if st.failover_limitation() is None:
                return None
        return 'failover is not possible: no good candidates have been found'