def all_facts(content):
    host = find_obj(content, [vim.HostSystem], None)
    ansible_facts = {}
    ansible_facts.update(get_cpu_facts(host))
    ansible_facts.update(get_memory_facts(host))
    ansible_facts.update(get_datastore_facts(host))
    ansible_facts.update(get_network_facts(host))
    ansible_facts.update(get_system_facts(host))
    return ansible_facts