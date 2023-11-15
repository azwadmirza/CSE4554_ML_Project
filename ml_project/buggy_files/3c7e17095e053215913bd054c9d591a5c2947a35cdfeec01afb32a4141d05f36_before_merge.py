def get_memory_facts(host):
    facts = {
        'ansible_memfree_mb': host.hardware.memorySize // 1024 // 1024 - host.summary.quickStats.overallMemoryUsage,
        'ansible_memtotal_mb': host.hardware.memorySize // 1024 // 1024,
    }
    return facts