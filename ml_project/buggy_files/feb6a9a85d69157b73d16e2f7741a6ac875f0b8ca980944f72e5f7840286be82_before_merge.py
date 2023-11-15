def _get_node(name=None, instance_id=None, location=None):
    if location is None:
        location = get_location()

    params = {'Action': 'DescribeInstances'}

    if str(name).startswith('i-') and (len(name) == 10 or len(name) == 19):
        instance_id = name

    if instance_id:
        params['InstanceId.1'] = instance_id
    else:
        params['Filter.1.Name'] = 'tag:Name'
        params['Filter.1.Value.1'] = name

    log.trace(params)

    provider = get_provider()

    attempts = 10
    while attempts >= 0:
        try:
            instances = aws.query(params,
                                  location=location,
                                  provider=provider,
                                  opts=__opts__,
                                  sigver='4')
            return _extract_instance_info(instances).values()[0]
        except IndexError:
            attempts -= 1
            log.debug(
                'Failed to get the data for node \'{0}\'. Remaining '
                'attempts: {1}'.format(
                    instance_id or name, attempts
                )
            )
            # Just a little delay between attempts...
            time.sleep(0.5)
    return {}