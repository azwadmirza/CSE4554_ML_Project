def show_instance(name=None, instance_id=None, call=None, kwargs=None):
    '''
    Show the details from EC2 concerning an AMI.

    Can be called as an action (which requires a name):

    .. code-block:: bash

        salt-cloud -a show_instance myinstance

    ...or as a function (which requires either a name or instance_id):

    .. code-block:: bash

        salt-cloud -f show_instance my-ec2 name=myinstance
        salt-cloud -f show_instance my-ec2 instance_id=i-d34db33f
    '''
    if not name and call == 'action':
        raise SaltCloudSystemExit(
            'The show_instance action requires a name.'
        )

    if call == 'function':
        name = kwargs.get('name', None)
        instance_id = kwargs.get('instance_id', None)

    if not name and not instance_id:
        raise SaltCloudSystemExit(
            'The show_instance function requires '
            'either a name or an instance_id'
        )

    node = _get_node(name=name, instance_id=instance_id)
    salt.utils.cloud.cache_node(node, __active_provider_name__, __opts__)
    return node