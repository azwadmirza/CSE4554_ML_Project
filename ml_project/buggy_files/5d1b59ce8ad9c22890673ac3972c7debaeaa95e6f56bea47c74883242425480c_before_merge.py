def _nic_profile(profile, hypervisor):
    '''
    Gather the nic profile from the config or apply the default based
    on the active hypervisor

    This is the ``default`` profile for KVM/QEMU, which can be
    overridden in the configuration:

    .. code-block:: yaml

        virt:
          nic:
            default:
              eth0:
                bridge: br0
                model: virtio

    The ``model`` parameter is optional, and will default to whatever
    is best suitable for the active hypervisor.
    '''
    default = {'eth0': {}}
    if hypervisor in ['esxi', 'vmware']:
        overlay = {'bridge': 'DEFAULT', 'model': 'e1000'}
    elif hypervisor in ['qemu', 'kvm']:
        overlay = {'bridge': 'br0', 'model': 'virtio'}
    else:
        overlay = {}
    nics = __salt__['config.get']('virt:nic', {}).get(profile, default)
    for key, val in overlay.items():
        for nic in nics:
            if key not in nics[nic]:
                nics[nic][key] = val
    return nics