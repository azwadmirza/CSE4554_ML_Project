def get_cpu_facts(host):
    facts = {
        'ansible_processor': host.summary.hardware.cpuModel,
        'ansible_processor_cores': host.summary.hardware.numCpuCores,
        'ansible_processor_count': host.summary.hardware.numCpuPkgs,
        'ansible_processor_vcpus': host.summary.hardware.numCpuThreads,
    }
    return facts