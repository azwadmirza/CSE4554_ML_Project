    def populate(self):
        self.module.run_command_environ_update = {'LANG': 'C', 'LC_ALL': 'C', 'LC_NUMERIC': 'C'}
        self.get_cpu_facts()
        self.get_memory_facts()
        self.get_dmi_facts()
        self.get_device_facts()
        self.get_uptime_facts()
        try:
            self.get_mount_facts()
        except TimeoutError:
            pass
        return self.facts