def create(name, allocated_storage, db_instance_class, engine,
           master_username, master_user_password, db_name=None,
           db_security_groups=None, vpc_security_group_ids=None,
           vpc_security_groups=None, availability_zone=None,
           db_subnet_group_name=None, preferred_maintenance_window=None,
           db_parameter_group_name=None, backup_retention_period=None,
           preferred_backup_window=None, port=None, multi_az=None,
           engine_version=None, auto_minor_version_upgrade=None,
           license_model=None, iops=None, option_group_name=None,
           character_set_name=None, publicly_accessible=None, wait_status=None,
           tags=None, db_cluster_identifier=None, storage_type=None,
           tde_credential_arn=None, tde_credential_password=None,
           storage_encrypted=None, kms_key_id=None, domain=None,
           copy_tags_to_snapshot=None, monitoring_interval=None,
           monitoring_role_arn=None, domain_iam_role_name=None, region=None,
           promotion_tier=None, key=None, keyid=None, profile=None):
    '''
    Create an RDS Instance

    CLI example to create an RDS Instance::

        salt myminion boto_rds.create myrds 10 db.t2.micro MySQL sqlusr sqlpassw
    '''
    if not allocated_storage:
        raise SaltInvocationError('allocated_storage is required')
    if not db_instance_class:
        raise SaltInvocationError('db_instance_class is required')
    if not engine:
        raise SaltInvocationError('engine is required')
    if not master_username:
        raise SaltInvocationError('master_username is required')
    if not master_user_password:
        raise SaltInvocationError('master_user_password is required')
    if availability_zone and multi_az:
        raise SaltInvocationError('availability_zone and multi_az are mutually'
                                  ' exclusive arguments.')
    if wait_status:
        wait_stati = ['available', 'modifying', 'backing-up']
        if wait_status not in wait_stati:
            raise SaltInvocationError('wait_status can be one of: '
                                      '{0}'.format(wait_stati))
    if vpc_security_groups:
        v_tmp = __salt__['boto_secgroup.convert_to_group_ids'](
                groups=vpc_security_groups, region=region, key=key, keyid=keyid,
                profile=profile)
        vpc_security_group_ids = (vpc_security_group_ids + v_tmp
                                  if vpc_security_group_ids else v_tmp)

    try:
        conn = _get_conn(region=region, key=key, keyid=keyid, profile=profile)
        if not conn:
            return {'results': bool(conn)}

        kwargs = {}
        boto_params = set(boto3_param_map.keys())
        keys = set(locals().keys())
        tags = _tag_doc(tags)

        for param_key in keys.intersection(boto_params):
            val = locals()[param_key]
            if val is not None:
                mapped = boto3_param_map[param_key]
                kwargs[mapped[0]] = mapped[1](val)

        # Validation doesn't want parameters that are None
        # https://github.com/boto/boto3/issues/400
        kwargs = dict((k, v) for k, v in six.iteritems(kwargs) if v is not None)

        rds = conn.create_db_instance(**kwargs)

        if not rds:
            return {'created': False}
        if not wait_status:
            return {'created': True, 'message':
                    'RDS instance {0} created.'.format(name)}

        while True:
            jmespath = 'DBInstances[*].DBInstanceStatus'
            status = describe_db_instances(name=name, jmespath=jmespath,
                                           region=region, key=key, keyid=keyid,
                                           profile=profile)
            if len(status):
                stat = status[0]
            else:
                # Whoops, something is horribly wrong...
                return {'created': False,
                        'error': "RDS instance {0} should have been created but"
                                 " now I can't find it.".format(name)}
            if stat == wait_status:
                return {'created': True,
                        'message': 'RDS instance {0} created (current status '
                        '{1})'.format(name, stat)}
            time.sleep(10)
            log.info('Instance status after 10 seconds is: {0}'.format(stat))

    except ClientError as e:
        return {'error': salt.utils.boto3.get_error(e)}