    def all_facts(self):
        ansible_facts = {}
        ansible_facts.update(self.get_cpu_facts())
        ansible_facts.update(self.get_memory_facts())
        ansible_facts.update(self.get_datastore_facts())
        ansible_facts.update(self.get_network_facts())
        ansible_facts.update(self.get_system_facts())
        self.module.exit_json(changed=False, ansible_facts=ansible_facts)