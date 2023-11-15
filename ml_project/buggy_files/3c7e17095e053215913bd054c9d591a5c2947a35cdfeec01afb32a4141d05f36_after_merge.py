    def get_memory_facts(self):
        return {
            'ansible_memfree_mb': self.host.hardware.memorySize // 1024 // 1024 - self.host.summary.quickStats.overallMemoryUsage,
            'ansible_memtotal_mb': self.host.hardware.memorySize // 1024 // 1024,
        }