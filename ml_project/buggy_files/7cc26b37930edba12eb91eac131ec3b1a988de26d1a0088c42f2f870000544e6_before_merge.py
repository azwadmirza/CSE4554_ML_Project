def get_resources_vms(call=None, resFilter=None, includeConfig=True):
    """
    Retrieve all VMs available on this environment

    CLI Example:

    .. code-block:: bash

        salt-cloud -f get_resources_vms my-proxmox-config
    """
    log.debug("Getting resource: vms.. (filter: %s)", resFilter)
    resources = query("get", "cluster/resources")

    ret = {}
    for resource in resources:
        if "type" in resource and resource["type"] in ["openvz", "qemu", "lxc"]:
            name = resource["name"]
            ret[name] = resource

            if includeConfig:
                # Requested to include the detailed configuration of a VM
                ret[name]["config"] = get_vmconfig(
                    ret[name]["vmid"], ret[name]["node"], ret[name]["type"]
                )

    if resFilter is not None:
        log.debug("Filter given: %s, returning requested " "resource: nodes", resFilter)
        return ret[resFilter]

    log.debug("Filter not given: %s, returning all resource: nodes", ret)
    return ret