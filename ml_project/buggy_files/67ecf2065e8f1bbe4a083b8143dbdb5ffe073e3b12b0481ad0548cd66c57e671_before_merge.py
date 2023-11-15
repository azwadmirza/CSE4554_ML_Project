def instance_info(since):
    info = {}
    instances = models.Instance.objects.values_list('hostname').values(
        'uuid', 'version', 'capacity', 'cpu', 'memory', 'managed_by_policy', 'hostname', 'last_isolated_check', 'enabled')
    for instance in instances:
        instance_info = {
            'uuid': instance['uuid'],
            'version': instance['version'],
            'capacity': instance['capacity'],
            'cpu': instance['cpu'],
            'memory': instance['memory'],
            'managed_by_policy': instance['managed_by_policy'],
            'last_isolated_check': instance['last_isolated_check'],
            'enabled': instance['enabled']
        }
        info[instance['uuid']] = instance_info
    return info