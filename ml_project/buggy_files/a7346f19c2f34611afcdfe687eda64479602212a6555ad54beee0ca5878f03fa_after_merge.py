def instance_present(name, instance_name=None, instance_id=None, image_id=None,
                     image_name=None, tags=None, key_name=None,
                     security_groups=None, user_data=None, instance_type=None,
                     placement=None, kernel_id=None, ramdisk_id=None,
                     vpc_id=None, vpc_name=None, monitoring_enabled=None,
                     subnet_id=None, subnet_name=None, private_ip_address=None,
                     block_device_map=None, disable_api_termination=None,
                     instance_initiated_shutdown_behavior=None,
                     placement_group=None, client_token=None,
                     security_group_ids=None, security_group_names=None,
                     additional_info=None, tenancy=None,
                     instance_profile_arn=None, instance_profile_name=None,
                     ebs_optimized=None, network_interfaces=None,
                     network_interface_name=None,
                     network_interface_id=None,
                     attributes=None, target_state=None, public_ip=None,
                     allocation_id=None, allocate_eip=False, region=None,
                     key=None, keyid=None, profile=None):
    ### TODO - implement 'target_state={running, stopped}'
    '''
    Ensure an EC2 instance is running with the given attributes and state.

    name
        (string) - The name of the state definition.  Recommended that this
        match the instance_name attribute (generally the FQDN of the instance).
    instance_name
        (string) - The name of the instance, generally its FQDN.  Exclusive with
        'instance_id'.
    instance_id
        (string) - The ID of the instance (if known).  Exclusive with
        'instance_name'.
    image_id
        (string) – The ID of the AMI image to run.
    image_name
        (string) – The name of the AMI image to run.
    tags
        (dict) - Tags to apply to the instance.
    key_name
        (string) – The name of the key pair with which to launch instances.
    security_groups
        (list of strings) – The names of the EC2 classic security groups with
        which to associate instances
    user_data
        (string) – The Base64-encoded MIME user data to be made available to the
        instance(s) in this reservation.
    instance_type
        (string) – The EC2 instance size/type.  Note that only certain types are
        compatible with HVM based AMIs.
    placement
        (string) – The Availability Zone to launch the instance into.
    kernel_id
        (string) – The ID of the kernel with which to launch the instances.
    ramdisk_id
        (string) – The ID of the RAM disk with which to launch the instances.
    vpc_id
        (string) - The ID of a VPC to attach the instance to.
    vpc_name
        (string) - The name of a VPC to attach the instance to.
    monitoring_enabled
        (bool) – Enable detailed CloudWatch monitoring on the instance.
    subnet_id
        (string) – The ID of the subnet within which to launch the instances for
        VPC.
    subnet_name
        (string) – The name of the subnet within which to launch the instances
        for VPC.
    private_ip_address
        (string) – If you’re using VPC, you can optionally use this parameter to
        assign the instance a specific available IP address from the subnet
        (e.g., 10.0.0.25).
    block_device_map
        (boto.ec2.blockdevicemapping.BlockDeviceMapping) – A BlockDeviceMapping
        data structure describing the EBS volumes associated with the Image.
    disable_api_termination
        (bool) – If True, the instances will be locked and will not be able to
        be terminated via the API.
    instance_initiated_shutdown_behavior
        (string) – Specifies whether the instance stops or terminates on
        instance-initiated shutdown. Valid values are:
            - 'stop'
            - 'terminate'
    placement_group
        (string) – If specified, this is the name of the placement group in
        which the instance(s) will be launched.
    client_token
        (string) – Unique, case-sensitive identifier you provide to ensure
        idempotency of the request. Maximum 64 ASCII characters.
    security_group_ids
        (list of strings) – The IDs of the VPC security groups with which to
        associate instances.
    security_group_names
        (list of strings) – The names of the VPC security groups with which to
        associate instances.
    additional_info
        (string) – Specifies additional information to make available to the
        instance(s).
    tenancy
        (string) – The tenancy of the instance you want to launch. An instance
        with a tenancy of ‘dedicated’ runs on single-tenant hardware and can
        only be launched into a VPC. Valid values are:”default” or “dedicated”.
        NOTE: To use dedicated tenancy you MUST specify a VPC subnet-ID as well.
    instance_profile_arn
        (string) – The Amazon resource name (ARN) of the IAM Instance Profile
        (IIP) to associate with the instances.
    instance_profile_name
        (string) – The name of the IAM Instance Profile (IIP) to associate with
        the instances.
    ebs_optimized
        (bool) – Whether the instance is optimized for EBS I/O. This
        optimization provides dedicated throughput to Amazon EBS and a tuned
        configuration stack to provide optimal EBS I/O performance. This
        optimization isn’t available with all instance types.
    network_interfaces
        (boto.ec2.networkinterface.NetworkInterfaceCollection) – A
        NetworkInterfaceCollection data structure containing the ENI
        specifications for the instance.
    network_interface_name
         (string) - The name of Elastic Network Interface to attach

        .. versionadded:: 2016.11.0

    network_interface_id
         (string) - The id of Elastic Network Interface to attach

        .. versionadded:: 2016.11.0

    attributes
        (dict) - Instance attributes and value to be applied to the instance.
        Available options are:
            - instanceType - A valid instance type (m1.small)
            - kernel - Kernel ID (None)
            - ramdisk - Ramdisk ID (None)
            - userData - Base64 encoded String (None)
            - disableApiTermination - Boolean (true)
            - instanceInitiatedShutdownBehavior - stop|terminate
            - blockDeviceMapping - List of strings - ie: [‘/dev/sda=false’]
            - sourceDestCheck - Boolean (true)
            - groupSet - Set of Security Groups or IDs
            - ebsOptimized - Boolean (false)
            - sriovNetSupport - String - ie: ‘simple’
    target_state
        (string) - The desired target state of the instance.  Available options
        are:
            - running
            - stopped
        Note that this option is currently UNIMPLEMENTED.
    public_ip:
        (string) - The IP of a previously allocated EIP address, which will be
        attached to the instance.  EC2 Classic instances ONLY - for VCP pass in
        an allocation_id instead.
    allocation_id:
        (string) - The ID of a previously allocated EIP address, which will be
        attached to the instance.  VPC instances ONLY - for Classic pass in
        a public_ip instead.
    allocate_eip:
        (bool) - Allocate and attach an EIP on-the-fly for this instance.  Note
        you'll want to releaase this address when terminating the instance,
        either manually or via the 'release_eip' flag to 'instance_absent'.
    region
        (string) - Region to connect to.
    key
        (string) - Secret key to be used.
    keyid
        (string) - Access key to be used.
    profile
        (variable) - A dict with region, key and keyid, or a pillar key (string)
        that contains a dict with region, key and keyid.

    .. versionadded:: 2016.3.0
    '''
    ret = {'name': name,
           'result': True,
           'comment': '',
           'changes': {}
          }
    _create = False
    running_states = ('pending', 'rebooting', 'running', 'stopping', 'stopped')
    changed_attrs = {}

    if not salt.utils.exactly_one((image_id, image_name)):
        raise SaltInvocationError('Exactly one of image_id OR '
                                  'image_name must be provided.')
    if (public_ip or allocation_id or allocate_eip) and not salt.utils.exactly_one((public_ip, allocation_id, allocate_eip)):
        raise SaltInvocationError('At most one of public_ip, allocation_id OR '
                                  'allocate_eip may be provided.')

    if instance_id:
        exists = __salt__['boto_ec2.exists'](instance_id=instance_id, region=region, key=key,
                                             keyid=keyid, profile=profile, in_states=running_states)
        if not exists:
            _create = True
    else:
        instances = __salt__['boto_ec2.find_instances'](name=instance_name if instance_name else name,
                                                        region=region, key=key, keyid=keyid, profile=profile,
                                                        in_states=running_states)
        if not len(instances):
            _create = True

    if _create:
        if __opts__['test']:
            ret['comment'] = 'The instance {0} is set to be created.'.format(name)
            ret['result'] = None
            return ret
        if image_name:
            args = {'ami_name': image_name, 'region': region, 'key': key,
                    'keyid': keyid, 'profile': profile}
            image_ids = __salt__['boto_ec2.find_images'](**args)
            if len(image_ids):
                image_id = image_ids[0]
            else:
                image_id = image_name
        r = __salt__['boto_ec2.run'](image_id, instance_name if instance_name else name,
                                     tags=tags, key_name=key_name,
                                     security_groups=security_groups, user_data=user_data,
                                     instance_type=instance_type, placement=placement,
                                     kernel_id=kernel_id, ramdisk_id=ramdisk_id, vpc_id=vpc_id,
                                     vpc_name=vpc_name, monitoring_enabled=monitoring_enabled,
                                     subnet_id=subnet_id, subnet_name=subnet_name,
                                     private_ip_address=private_ip_address,
                                     block_device_map=block_device_map,
                                     disable_api_termination=disable_api_termination,
                                     instance_initiated_shutdown_behavior=instance_initiated_shutdown_behavior,
                                     placement_group=placement_group, client_token=client_token,
                                     security_group_ids=security_group_ids,
                                     security_group_names=security_group_names,
                                     additional_info=additional_info, tenancy=tenancy,
                                     instance_profile_arn=instance_profile_arn,
                                     instance_profile_name=instance_profile_name,
                                     ebs_optimized=ebs_optimized, network_interfaces=network_interfaces,
                                     network_interface_name=network_interface_name,
                                     network_interface_id=network_interface_id,
                                     region=region, key=key, keyid=keyid, profile=profile)
        if not r or 'instance_id' not in r:
            ret['result'] = False
            ret['comment'] = 'Failed to create instance {0}.'.format(instance_name if instance_name else name)
            return ret

        instance_id = r['instance_id']
        ret['changes'] = {'old': {}, 'new': {}}
        ret['changes']['old']['instance_id'] = None
        ret['changes']['new']['instance_id'] = instance_id

        # To avoid issues we only allocate new EIPs at instance creation.
        # This might miss situations where an instance is initially created
        # created without and one is added later, but the alternative is the
        # risk of EIPs allocated at every state run.
        if allocate_eip:
            if __opts__['test']:
                ret['comment'] = 'New EIP would be allocated.'
                ret['result'] = None
                return ret
            domain = 'vpc' if vpc_id or vpc_name else None
            r = __salt__['boto_ec2.allocate_eip_address'](
                    domain=domain, region=region, key=key, keyid=keyid,
                    profile=profile)
            if not r:
                ret['result'] = False
                ret['comment'] = 'Failed to allocate new EIP.'
                return ret
            allocation_id = r['allocation_id']
            log.info("New EIP with address {0} allocated.".format(r['public_ip']))
        else:
            log.info("EIP not requested.")

    if public_ip or allocation_id:
        # This can take a bit to show up, give it a chance to...
        tries = 10
        secs = 3
        for t in range(tries):
            r = __salt__['boto_ec2.get_eip_address_info'](
                    addresses=public_ip, allocation_ids=allocation_id,
                    region=region, key=key, keyid=keyid, profile=profile)
            if r:
                break
            else:
                log.info("Waiting up to {0} secs for new EIP {1} to become available".format(
                        tries * secs, public_ip or allocation_id))
                time.sleep(secs)
        if not r:
            ret['result'] = False
            ret['comment'] = 'Failed to lookup EIP {0}.'.format(public_ip or allocation_id)
            return ret
        ip = r[0]['public_ip']
        if r[0].get('instance_id'):
            if r[0]['instance_id'] != instance_id:
                ret['result'] = False
                ret['comment'] = ('EIP {0} is already associated with instance '
                                  '{1}.'.format(public_ip if public_ip else
                                  allocation_id, r[0]['instance_id']))
                return ret
        else:
            if __opts__['test']:
                ret['comment'] = 'Instance {0} to be updated.'.format(name)
                ret['result'] = None
                return ret
            r = __salt__['boto_ec2.associate_eip_address'](
                    instance_id=instance_id, public_ip=public_ip,
                    allocation_id=allocation_id, region=region, key=key,
                    keyid=keyid, profile=profile)
            if r:
                if 'new' not in ret['changes']:
                    ret['changes']['new'] = {}
                ret['changes']['new']['public_ip'] = ip
            else:
                ret['result'] = False
                ret['comment'] = 'Failed to attach EIP to instance {0}.'.format(
                        instance_name if instance_name else name)
                return ret

    if attributes:
        for k, v in six.iteritems(attributes):
            curr = __salt__['boto_ec2.get_attribute'](k, instance_id=instance_id, region=region, key=key,
                                                      keyid=keyid, profile=profile)
            if not isinstance(curr, dict):
                curr = {}
            if curr.get(k) == v:
                continue
            else:
                if __opts__['test']:
                    changed_attrs[k] = 'The instance attribute {0} is set to be changed from \'{1}\' to \'{2}\'.'.format(
                                       k, curr.get(k), v)
                    continue
                try:
                    r = __salt__['boto_ec2.set_attribute'](attribute=k, attribute_value=v,
                                                           instance_id=instance_id, region=region,
                                                           key=key, keyid=keyid, profile=profile)
                except SaltInvocationError as e:
                    ret['result'] = False
                    ret['comment'] = 'Failed to set attribute {0} to {1} on instance {2}.'.format(k, v, instance_name)
                    return ret
                ret['changes'] = ret['changes'] if ret['changes'] else {'old': {}, 'new': {}}
                ret['changes']['old'][k] = curr.get(k)
                ret['changes']['new'][k] = v

    if __opts__['test']:
        if changed_attrs:
            ret['changes']['new'] = changed_attrs
            ret['result'] = None
        else:
            ret['comment'] = 'Instance {0} is in the correct state'.format(instance_name if instance_name else name)
            ret['result'] = True

    return ret