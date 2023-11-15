def find_vm_by_id(content, vm_id, vm_id_type="vm_name", datacenter=None, cluster=None):
    """ UUID is unique to a VM, every other id returns the first match. """
    si = content.searchIndex
    vm = None

    if vm_id_type == 'dns_name':
        vm = si.FindByDnsName(datacenter=datacenter, dnsName=vm_id, vmSearch=True)
    elif vm_id_type == 'inventory_path':
        vm = si.FindByInventoryPath(inventoryPath=vm_id)
        if isinstance(vm, vim.VirtualMachine):
            vm = None
    elif vm_id_type == 'uuid':
        vm = si.FindByUuid(datacenter=datacenter, instanceUuid=vm_id, vmSearch=True)
    elif vm_id_type == 'ip':
        vm = si.FindByIp(datacenter=datacenter, ip=vm_id, vmSearch=True)
    elif vm_id_type == 'vm_name':
        folder = None
        if cluster:
            folder = cluster
        elif datacenter:
            folder = datacenter.hostFolder
        vm = find_vm_by_name(content, vm_id, folder)

    return vm