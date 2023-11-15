def set_attributes(name, attributes, region=None, key=None, keyid=None,
                   profile=None):
    '''
    Set attributes on an ELB.

    name (string)
        Name of the ELB instance to set attributes for

    attributes
        A dict of attributes to set.

        Valid attributes are:

        access_log (dict)
            enabled (bool)
                Enable storage of access logs.
            s3_bucket_name (string)
                The name of the S3 bucket to place logs.
            s3_bucket_prefix (string)
                Prefix for the log file name.
            emit_interval (int)
                Interval for storing logs in S3 in minutes. Valid values are
                5 and 60.

        connection_draining (dict)
            enabled (bool)
                Enable connection draining.
            timeout (int)
                Maximum allowed time in seconds for sending existing
                connections to an instance that is deregistering or unhealthy.
                Default is 300.

        cross_zone_load_balancing (dict)
            enabled (bool)
                Enable cross-zone load balancing.

    CLI example to set attributes on an ELB:

    .. code-block:: bash

        salt myminion boto_elb.set_attributes myelb '{"access_log": {"enabled": "true", "s3_bucket_name": "mybucket", "s3_bucket_prefix": "mylogs/", "emit_interval": "5"}}' region=us-east-1
    '''
    conn = _get_conn(region=region, key=key, keyid=keyid, profile=profile)

    al = attributes.get('access_log', {})
    czlb = attributes.get('cross_zone_load_balancing', {})
    cd = attributes.get('connection_draining', {})
    cs = attributes.get('connecting_settings', {})
    if not al and not czlb and not cd and not cs:
        log.error('No supported attributes for ELB.')
        return False
    if al:
        _al = AccessLogAttribute()
        _al.enabled = al.get('enabled', False)
        if not _al.enabled:
            msg = 'Access log attribute configured, but enabled config missing'
            log.error(msg)
            return False
        _al.s3_bucket_name = al.get('s3_bucket_name', None)
        _al.s3_bucket_prefix = al.get('s3_bucket_prefix', None)
        _al.emit_interval = al.get('emit_interval', None)
        added_attr = conn.modify_lb_attribute(name, 'accessLog', _al)
        if added_attr:
            log.info('Added access_log attribute to {0} elb.'.format(name))
        else:
            msg = 'Failed to add access_log attribute to {0} elb.'
            log.error(msg.format(name))
            return False
    if czlb:
        _czlb = CrossZoneLoadBalancingAttribute()
        _czlb.enabled = czlb['enabled']
        added_attr = conn.modify_lb_attribute(name, 'crossZoneLoadBalancing',
                                              _czlb.enabled)
        if added_attr:
            msg = 'Added cross_zone_load_balancing attribute to {0} elb.'
            log.info(msg.format(name))
        else:
            log.error('Failed to add cross_zone_load_balancing attribute.')
            return False
    if cd:
        _cd = ConnectionDrainingAttribute()
        _cd.enabled = cd['enabled']
        _cd.timeout = cd.get('timeout', 300)
        added_attr = conn.modify_lb_attribute(name, 'connectionDraining', _cd)
        if added_attr:
            msg = 'Added connection_draining attribute to {0} elb.'
            log.info(msg.format(name))
        else:
            log.error('Failed to add connection_draining attribute.')
            return False
    if cs:
        _cs = ConnectionSettingAttribute()
        _cs.idle_timeout = cs.get('idle_timeout', 60)
        added_attr = conn.modify_lb_attribute(name, 'connectingSettings', _cs)
        if added_attr:
            msg = 'Added connecting_settings attribute to {0} elb.'
            log.info(msg.format(name))
        else:
            log.error('Failed to add connecting_settings attribute.')
            return False
    return True