def _toggle_delvol(name=None, instance_id=None, device=None, volume_id=None,
                   value=None, requesturl=None):

    if not instance_id:
        instances = list_nodes_full(get_location())
        instance_id = instances[name]['instanceId']

    if requesturl:
        data = query(requesturl=requesturl)
    else:
        params = {'Action': 'DescribeInstances',
                  'InstanceId.1': instance_id}
        data, requesturl = query(                       # pylint: disable=W0632
            params, return_url=True)

    blockmap = data[0]['instancesSet']['item']['blockDeviceMapping']

    params = {'Action': 'ModifyInstanceAttribute',
              'InstanceId': instance_id}

    if type(blockmap['item']) != list:
        blockmap['item'] = [blockmap['item']]

    for idx, item in enumerate(blockmap['item']):
        device_name = item['deviceName']

        if device is not None and device != device_name:
            continue
        if volume_id is not None and volume_id != item['ebs']['volumeId']:
            continue

        params['BlockDeviceMapping.{0}.DeviceName'.format(idx)] = device_name
        params['BlockDeviceMapping.{0}.Ebs.DeleteOnTermination'.format(idx)] = value

    query(params, return_root=True)

    return query(requesturl=requesturl)