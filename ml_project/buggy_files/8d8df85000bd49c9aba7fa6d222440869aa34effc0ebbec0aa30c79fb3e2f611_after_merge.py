def queue_instances(instances):
    '''
    Queue a set of instances to be provisioned later. Expects a list.

    Currently this only queries node data, and then places it in the cloud
    cache (if configured). If the salt-cloud-reactor is being used, these
    instances will be automatically provisioned using that.

    For more information about the salt-cloud-reactor, see:

    https://github.com/saltstack-formulas/salt-cloud-reactor
    '''
    for instance_id in instances:
        node = _get_node(instance_id=instance_id)
        for name in node:
            if instance_id == node[name]['instanceId']:
                salt.utils.cloud.cache_node(node[name],
                                            __active_provider_name__,
                                            __opts__)