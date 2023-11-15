    def __init__(self, results, runner):
        self.runner = runner

        self.results = { 'contacted': {}, 'dark': {}}
        self.hosts_to_poll = []
        self.completed = False

        # flag to determine if at least one host was contacted
        self.active = False
        # True to work with the `and` below
        skipped = True
        jid = None
        for (host, res) in results['contacted'].iteritems():
            if res.get('started', False):
                self.hosts_to_poll.append(host)
                jid = res.get('ansible_job_id', None)
                self.runner.vars_cache[host]['ansible_job_id'] = jid
                self.active = True
            else:
                skipped = skipped and res.get('skipped', False)
                self.results['contacted'][host] = res
        for (host, res) in results['dark'].iteritems():
            self.runner.vars_cache[host]['ansible_job_id'] = ''
            self.results['dark'][host] = res

        if not skipped:
            if jid is None:
                raise errors.AnsibleError("unexpected error: unable to determine jid")
            if len(self.hosts_to_poll)==0:
                raise errors.AnsibleError("unexpected error: no hosts to poll")