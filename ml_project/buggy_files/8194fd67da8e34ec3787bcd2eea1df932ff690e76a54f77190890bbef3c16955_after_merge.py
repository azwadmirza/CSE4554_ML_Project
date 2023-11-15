    def get_cpu_facts(self):
        return {
            'ansible_processor': self.host.summary.hardware.cpuModel,
            'ansible_processor_cores': self.host.summary.hardware.numCpuCores,
            'ansible_processor_count': self.host.summary.hardware.numCpuPkgs,
            'ansible_processor_vcpus': self.host.summary.hardware.numCpuThreads,
        }