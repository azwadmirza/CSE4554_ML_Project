def present(name,
            allocated_storage,
            db_instance_class,
            engine,
            master_username,
            master_user_password,
            db_name=None,
            db_security_groups=None,
            vpc_security_group_ids=None,
            availability_zone=None,
            db_subnet_group_name=None,
            preferred_maintenance_window=None,
            db_parameter_group_name=None,
            backup_retention_period=None,
            preferred_backup_window=None,
            port=None,
            multi_az=None,
            engine_version=None,
            auto_minor_version_upgrade=None,
            license_model=None,
            iops=None,
            option_group_name=None,
            character_set_name=None,
            publicly_accessible=None,
            wait_status=None,
            tags=None,
            region=None,
            key=None,
            keyid=None,
            profile=None):
    '''
    Ensure RDS instance exists.

    name
        Name of the RDS instance.

    allocated_storage
        The amount of storage (in gigabytes) to be initially allocated for the
        database instance.

    db_instance_class
        The compute and memory capacity of the Amazon RDS DB instance.

    engine
        The name of the database engine to be used for this instance.

    master_username
        The name of master user for the client DB instance.

    master_user_password
        The password for the master database user. Can be any printable ASCII
        character except "/", '"', or "@".

    db_name
        The database name for the restored DB instance.

    db_security_groups
        A list of DB security groups to associate with this DB instance.

    vpc_security_group_ids
        A list of EC2 VPC security groups to associate with this DB instance.

    availability_zone
        The EC2 Availability Zone that the database instance will be created
        in.

    db_subnet_group_name
        A DB subnet group to associate with this DB instance.

    preferred_maintenance_window
        The weekly time range (in UTC) during which system maintenance can
        occur.

    backup_retention_period
        The number of days for which automated backups are retained.

    preferred_backup_window
        The daily time range during which automated backups are created if
        automated backups are enabled.

    port
        The port number on which the database accepts connections.

    multi_az
        Specifies if the DB instance is a Multi-AZ deployment. You cannot set
        the AvailabilityZone parameter if the MultiAZ parameter is set to true.

    engine_version
        The version number of the database engine to use.

    auto_minor_version_upgrade
        Indicates that minor engine upgrades will be applied automatically to
        the DB instance during the maintenance window.

    license_model
        License model information for this DB instance.

    iops
        The amount of Provisioned IOPS (input/output operations per second) to
        be initially allocated for the DB instance.

    option_group_name
        Indicates that the DB instance should be associated with the specified
        option group.

    character_set_name
        For supported engines, indicates that the DB instance should be
        associated with the specified CharacterSet.

    publicly_accessible
        Specifies the accessibility options for the DB instance. A value of
        true specifies an Internet-facing instance with a publicly resolvable
        DNS name, which resolves to a public IP address. A value of false
        specifies an internal instance with a DNS name that resolves to a
        private IP address.

    wait_status
        Wait for the RDS instance to reach a disared status before finishing
        the state. Available states: available, modifying, backing-up

    tags
        A list of tags.

    region
        Region to connect to.

    key
        Secret key to be used.

    keyid
        Access key to be used.

    profile
        A dict with region, key and keyid, or a pillar key (string) that
        contains a dict with region, key and keyid.
    '''
    ret = {'name': name,
           'result': True,
           'comment': '',
           'changes': {}
           }
    _ret = _rds_present(name, allocated_storage,
                        db_instance_class, engine,
                        master_username, master_user_password, db_name,
                        db_security_groups, vpc_security_group_ids,
                        availability_zone, db_subnet_group_name,
                        preferred_maintenance_window, db_parameter_group_name,
                        backup_retention_period, preferred_backup_window, port,
                        multi_az, engine_version, auto_minor_version_upgrade,
                        license_model, iops, option_group_name,
                        character_set_name, publicly_accessible, wait_status,
                        tags, region, key, keyid, profile)
    ret['changes'] = _ret['changes']
    ret['comment'] = ' '.join([ret['comment'], _ret['comment']])
    if not _ret['result']:
        ret['result'] = _ret['result']
        if ret['result'] is False:
            return ret
    return ret