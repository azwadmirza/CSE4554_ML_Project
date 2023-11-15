def _rds_present(name, allocated_storage, storage_type, db_instance_class,
                 engine, master_username, master_user_password, db_name=None,
                 db_security_groups=None, vpc_security_group_ids=None,
                 availability_zone=None, db_subnet_group_name=None,
                 preferred_maintenance_window=None,
                 db_parameter_group_name=None, backup_retention_period=None,
                 preferred_backup_window=None, port=None, multi_az=None,
                 engine_version=None, auto_minor_version_upgrade=None,
                 license_model=None, iops=None, option_group_name=None,
                 character_set_name=None, publicly_accessible=None,
                 wait_status=None, tags=None, region=None, key=None,
                 keyid=None, profile=None):
    ret = {'result': True,
           'comment': '',
           'changes': {}
           }
    exists = __salt__['boto_rds.exists'](name, tags, region, key, keyid,
                                         profile)
    if not exists:
        if __opts__['test']:
            ret['comment'] = 'RDS {0} is set to be created.'.format(name)
            ret['result'] = None
            return ret
        created = __salt__['boto_rds.create'](name, allocated_storage,
                                              storage_type, db_instance_class,
                                              engine, master_username,
                                              master_user_password, db_name,
                                              db_security_groups,
                                              vpc_security_group_ids,
                                              availability_zone,
                                              db_subnet_group_name,
                                              preferred_maintenance_window,
                                              db_parameter_group_name,
                                              backup_retention_period,
                                              preferred_backup_window, port,
                                              multi_az, engine_version,
                                              auto_minor_version_upgrade,
                                              license_model, iops,
                                              option_group_name,
                                              character_set_name,
                                              publicly_accessible,
                                              wait_status, tags, region, key,
                                              keyid, profile)
        if not created:
            ret['result'] = False
            ret['comment'] = 'Failed to create {0} RDS.'.format(name)
            return ret
        _describe = __salt__['boto_rds.describe'](name, tags, region, key,
                                                  keyid, profile)
        ret['changes']['old'] = {'rds': None}
        ret['changes']['new'] = {'rds': _describe}
        ret['comment'] = 'RDS {0} created.'.format(name)
    else:
        ret['comment'] = 'RDS replica {0} exists.'.format(name)
    return ret