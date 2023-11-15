    def deploy(self):
        facts = {}

        if self.params['inject_ovf_env']:
            self.inject_ovf_env()

        if self.params['power_on']:
            task = self.entity.PowerOn()
            if self.params['wait']:
                wait_for_task(task)
                if self.params['wait_for_ip_address']:
                    _facts = wait_for_vm_ip(self.content, self.entity)
                    if not _facts:
                        self.module.fail_json(msg='Waiting for IP address timed out')
                    facts.update(_facts)

        if not facts:
            facts.update(gather_vm_facts(self.content, self.entity))

        return facts