    def get_datastore_facts(self):
        facts = dict()
        facts['ansible_datastore'] = []
        for store in self.host.datastore:
            _tmp = {
                'name': store.summary.name,
                'total': bytes_to_human(store.summary.capacity),
                'free': bytes_to_human(store.summary.freeSpace),
            }
            facts['ansible_datastore'].append(_tmp)
        return facts