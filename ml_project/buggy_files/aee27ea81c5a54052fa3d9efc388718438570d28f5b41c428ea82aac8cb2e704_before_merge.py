def get_system_facts(host):
    sn = 'NA'
    for info in host.hardware.systemInfo.otherIdentifyingInfo:
        if info.identifierType.key == 'ServiceTag':
            sn = info.identifierValue
    facts = {
        'ansible_distribution': host.config.product.name,
        'ansible_distribution_version': host.config.product.version,
        'ansible_distribution_build': host.config.product.build,
        'ansible_os_type': host.config.product.osType,
        'ansible_system_vendor': host.hardware.systemInfo.vendor,
        'ansible_hostname': host.summary.config.name,
        'ansible_product_name': host.hardware.systemInfo.model,
        'ansible_product_serial': sn,
        'ansible_bios_date': host.hardware.biosInfo.releaseDate,
        'ansible_bios_version': host.hardware.biosInfo.biosVersion,
    }
    return facts