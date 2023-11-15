def request_instance(vm_=None, call=None):
    '''
    Put together all of the information necessary to request an instance on EC2,
    and then fire off the request the instance.

    Returns data about the instance
    '''
    if call == 'function':
        # Technically this function may be called other ways too, but it
        # definitely cannot be called with --function.
        raise SaltCloudSystemExit(
            'The request_instance action must be called with -a or --action.'
        )

    location = vm_.get('location', get_location(vm_))

    # do we launch a regular vm or a spot instance?
    # see http://goo.gl/hYZ13f for more information on EC2 API
    spot_config = get_spot_config(vm_)
    if spot_config is not None:
        if 'spot_price' not in spot_config:
            raise SaltCloudSystemExit(
                'Spot instance config for {0} requires a spot_price '
                'attribute.'.format(vm_['name'])
            )

        params = {'Action': 'RequestSpotInstances',
                  'InstanceCount': '1',
                  'Type': spot_config['type']
                  if 'type' in spot_config else 'one-time',
                  'SpotPrice': spot_config['spot_price']}

        # All of the necessary launch parameters for a VM when using
        # spot instances are the same except for the prefix below
        # being tacked on.
        spot_prefix = 'LaunchSpecification.'

    # regular EC2 instance
    else:
        # WARNING! EXPERIMENTAL!
        # This allows more than one instance to be spun up in a single call.
        # The first instance will be called by the name provided, but all other
        # instances will be nameless (or more specifically, they will use the
        # InstanceId as the name). This interface is expected to change, so
        # use at your own risk.
        min_instance = config.get_cloud_config_value(
            'min_instance', vm_, __opts__, search_global=False, default=1
        )
        max_instance = config.get_cloud_config_value(
            'max_instance', vm_, __opts__, search_global=False, default=1
        )
        params = {'Action': 'RunInstances',
                  'MinCount': min_instance,
                  'MaxCount': max_instance}

        # Normal instances should have no prefix.
        spot_prefix = ''

    image_id = vm_['image']
    params[spot_prefix + 'ImageId'] = image_id

    userdata = None
    userdata_file = config.get_cloud_config_value(
        'userdata_file', vm_, __opts__, search_global=False, default=None
    )
    if userdata_file is None:
        userdata = config.get_cloud_config_value(
            'userdata', vm_, __opts__, search_global=False, default=None
        )
    else:
        log.trace('userdata_file: {0}'.format(userdata_file))
        if os.path.exists(userdata_file):
            with salt.utils.fopen(userdata_file, 'r') as fh_:
                userdata = fh_.read()

    userdata = salt.utils.cloud.userdata_template(__opts__, vm_, userdata)

    if userdata is not None:
        try:
            params[spot_prefix + 'UserData'] = base64.b64encode(userdata)
        except Exception as exc:
            log.exception('Failed to encode userdata: %s', exc)

    vm_size = config.get_cloud_config_value(
        'size', vm_, __opts__, search_global=False
    )
    params[spot_prefix + 'InstanceType'] = vm_size

    ex_keyname = keyname(vm_)
    if ex_keyname:
        params[spot_prefix + 'KeyName'] = ex_keyname

    ex_securitygroup = securitygroup(vm_)
    if ex_securitygroup:
        if not isinstance(ex_securitygroup, list):
            params[spot_prefix + 'SecurityGroup.1'] = ex_securitygroup
        else:
            for counter, sg_ in enumerate(ex_securitygroup):
                params[spot_prefix + 'SecurityGroup.{0}'.format(counter)] = sg_

    ex_iam_profile = iam_profile(vm_)
    if ex_iam_profile:
        try:
            if ex_iam_profile.startswith('arn:aws:iam:'):
                params[
                    spot_prefix + 'IamInstanceProfile.Arn'
                ] = ex_iam_profile
            else:
                params[
                    spot_prefix + 'IamInstanceProfile.Name'
                ] = ex_iam_profile
        except AttributeError:
            raise SaltCloudConfigError(
                '\'iam_profile\' should be a string value.'
            )

    az_ = get_availability_zone(vm_)
    if az_ is not None:
        params[spot_prefix + 'Placement.AvailabilityZone'] = az_

    tenancy_ = get_tenancy(vm_)
    if tenancy_ is not None:
        if spot_config is not None:
            raise SaltCloudConfigError(
                'Spot instance config for {0} does not support '
                'specifying tenancy.'.format(vm_['name'])
            )
        params['Placement.Tenancy'] = tenancy_

    subnetid_ = get_subnetid(vm_)
    if subnetid_ is not None:
        params[spot_prefix + 'SubnetId'] = subnetid_

    ex_securitygroupid = securitygroupid(vm_)
    if ex_securitygroupid:
        if not isinstance(ex_securitygroupid, list):
            params[spot_prefix + 'SecurityGroupId.1'] = ex_securitygroupid
        else:
            for counter, sg_ in enumerate(ex_securitygroupid):
                params[
                    spot_prefix + 'SecurityGroupId.{0}'.format(counter)
                ] = sg_

    placementgroup_ = get_placementgroup(vm_)
    if placementgroup_ is not None:
        params[spot_prefix + 'Placement.GroupName'] = placementgroup_

    ex_blockdevicemappings = block_device_mappings(vm_)
    if ex_blockdevicemappings:
        params.update(_param_from_config(spot_prefix + 'BlockDeviceMapping',
                      ex_blockdevicemappings))

    network_interfaces = config.get_cloud_config_value(
        'network_interfaces',
        vm_,
        __opts__,
        search_global=False
    )

    if network_interfaces:
        eni_devices = []
        for interface in network_interfaces:
            log.debug('Create network interface: {0}'.format(interface))
            _new_eni = _create_eni_if_necessary(interface, vm_)
            eni_devices.append(_new_eni)
        params.update(_param_from_config(spot_prefix + 'NetworkInterface',
                                         eni_devices))

    set_ebs_optimized = config.get_cloud_config_value(
        'ebs_optimized', vm_, __opts__, search_global=False
    )

    if set_ebs_optimized is not None:
        if not isinstance(set_ebs_optimized, bool):
            raise SaltCloudConfigError(
                '\'ebs_optimized\' should be a boolean value.'
            )
        params[spot_prefix + 'EbsOptimized'] = set_ebs_optimized

    set_del_root_vol_on_destroy = config.get_cloud_config_value(
        'del_root_vol_on_destroy', vm_, __opts__, search_global=False
    )

    if set_del_root_vol_on_destroy and not isinstance(set_del_root_vol_on_destroy, bool):
        raise SaltCloudConfigError(
            '\'del_root_vol_on_destroy\' should be a boolean value.'
        )

    vm_['set_del_root_vol_on_destroy'] = set_del_root_vol_on_destroy

    if set_del_root_vol_on_destroy:
        # first make sure to look up the root device name
        # as Ubuntu and CentOS (and most likely other OSs)
        # use different device identifiers

        log.info('Attempting to look up root device name for image id {0} on '
                 'VM {1}'.format(image_id, vm_['name']))

        rd_params = {
            'Action': 'DescribeImages',
            'ImageId.1': image_id
        }
        try:
            rd_data = aws.query(rd_params,
                                location=get_location(vm_),
                                provider=get_provider(),
                                opts=__opts__,
                                sigver='4')
            if 'error' in rd_data:
                return rd_data['error']
            log.debug('EC2 Response: \'{0}\''.format(rd_data))
        except Exception as exc:
            log.error(
                'Error getting root device name for image id {0} for '
                'VM {1}: \n{2}'.format(image_id, vm_['name'], exc),
                # Show the traceback if the debug logging level is enabled
                exc_info_on_loglevel=logging.DEBUG
            )
            raise

        # make sure we have a response
        if not rd_data:
            err_msg = 'There was an error querying EC2 for the root device ' \
                      'of image id {0}. Empty response.'.format(image_id)
            raise SaltCloudSystemExit(err_msg)

        # pull the root device name from the result and use it when
        # launching the new VM
        rd_name = None
        rd_type = None
        if 'blockDeviceMapping' in rd_data[0]:
            # Some ami instances do not have a root volume. Ignore such cases
            if rd_data[0]['blockDeviceMapping'] is not None:
                item = rd_data[0]['blockDeviceMapping']['item']
                if isinstance(item, list):
                    item = item[0]
                rd_name = item['deviceName']
                # Grab the volume type
                rd_type = item['ebs'].get('volumeType', None)

            log.info('Found root device name: {0}'.format(rd_name))

        if rd_name is not None:
            if ex_blockdevicemappings:
                dev_list = [
                    dev['DeviceName'] for dev in ex_blockdevicemappings
                ]
            else:
                dev_list = []

            if rd_name in dev_list:
                # Device already listed, just grab the index
                dev_index = dev_list.index(rd_name)
            else:
                dev_index = len(dev_list)
                # Add the device name in since it wasn't already there
                params[
                    '{0}BlockDeviceMapping.{1}.DeviceName'.format(
                        spot_prefix, dev_index
                    )
                ] = rd_name

            # Set the termination value
            termination_key = '{0}BlockDeviceMapping.{1}.Ebs.DeleteOnTermination'.format(spot_prefix, dev_index)
            params[termination_key] = str(set_del_root_vol_on_destroy).lower()

            # Use default volume type if not specified
            if ex_blockdevicemappings and 'Ebs.VolumeType' not in ex_blockdevicemappings[dev_index]:
                type_key = '{0}BlockDeviceMapping.{1}.Ebs.VolumeType'.format(spot_prefix, dev_index)
                params[type_key] = rd_type

    set_del_all_vols_on_destroy = config.get_cloud_config_value(
        'del_all_vols_on_destroy', vm_, __opts__, search_global=False, default=False
    )

    if set_del_all_vols_on_destroy and not isinstance(set_del_all_vols_on_destroy, bool):
        raise SaltCloudConfigError(
            '\'del_all_vols_on_destroy\' should be a boolean value.'
        )

    __utils__['cloud.fire_event'](
        'event',
        'requesting instance',
        'salt/cloud/{0}/requesting'.format(vm_['name']),
        args={
            'kwargs': __utils__['cloud.filter_event'](
                'requesting', params, list(params)
            ),
            'location': location,
        },
        sock_dir=__opts__['sock_dir'],
        transport=__opts__['transport']
    )

    provider = get_provider(vm_)

    try:
        data = aws.query(params,
                         'instancesSet',
                         location=location,
                         provider=provider,
                         opts=__opts__,
                         sigver='4')
        if 'error' in data:
            return data['error']
    except Exception as exc:
        log.error(
            'Error creating {0} on EC2 when trying to run the initial '
            'deployment: \n{1}'.format(
                vm_['name'], exc
            ),
            # Show the traceback if the debug logging level is enabled
            exc_info_on_loglevel=logging.DEBUG
        )
        raise

    # if we're using spot instances, we need to wait for the spot request
    # to become active before we continue
    if spot_config:
        sir_id = data[0]['spotInstanceRequestId']

        def __query_spot_instance_request(sir_id, location):
            params = {'Action': 'DescribeSpotInstanceRequests',
                      'SpotInstanceRequestId.1': sir_id}
            data = aws.query(params,
                             location=location,
                             provider=provider,
                             opts=__opts__,
                             sigver='4')
            if not data:
                log.error(
                    'There was an error while querying EC2. Empty response'
                )
                # Trigger a failure in the wait for spot instance method
                return False

            if isinstance(data, dict) and 'error' in data:
                log.warning(
                    'There was an error in the query. {0}'
                    .format(data['error'])
                )
                # Trigger a failure in the wait for spot instance method
                return False

            log.debug('Returned query data: {0}'.format(data))

            state = data[0].get('state')

            if state == 'active':
                return data

            if state == 'open':
                # Still waiting for an active state
                log.info('Spot instance status: {0}'.format(
                    data[0]['status']['message']
                ))
                return None

            if state in ['cancelled', 'failed', 'closed']:
                # Request will never be active, fail
                log.error('Spot instance request resulted in state \'{0}\'. '
                          'Nothing else we can do here.')
                return False

        __utils__['cloud.fire_event'](
            'event',
            'waiting for spot instance',
            'salt/cloud/{0}/waiting_for_spot'.format(vm_['name']),
            sock_dir=__opts__['sock_dir'],
            transport=__opts__['transport']
        )

        try:
            data = _wait_for_spot_instance(
                __query_spot_instance_request,
                update_args=(sir_id, location),
                timeout=config.get_cloud_config_value(
                    'wait_for_spot_timeout', vm_, __opts__, default=10 * 60),
                interval=config.get_cloud_config_value(
                    'wait_for_spot_interval', vm_, __opts__, default=30),
                interval_multiplier=config.get_cloud_config_value(
                    'wait_for_spot_interval_multiplier',
                    vm_,
                    __opts__,
                    default=1),
                max_failures=config.get_cloud_config_value(
                    'wait_for_spot_max_failures',
                    vm_,
                    __opts__,
                    default=10),
            )
            log.debug('wait_for_spot_instance data {0}'.format(data))

        except (SaltCloudExecutionTimeout, SaltCloudExecutionFailure) as exc:
            try:
                # Cancel the existing spot instance request
                params = {'Action': 'CancelSpotInstanceRequests',
                          'SpotInstanceRequestId.1': sir_id}
                data = aws.query(params,
                                 location=location,
                                 provider=provider,
                                 opts=__opts__,
                                 sigver='4')

                log.debug('Canceled spot instance request {0}. Data '
                          'returned: {1}'.format(sir_id, data))

            except SaltCloudSystemExit:
                pass
            finally:
                raise SaltCloudSystemExit(str(exc))

    return data, vm_