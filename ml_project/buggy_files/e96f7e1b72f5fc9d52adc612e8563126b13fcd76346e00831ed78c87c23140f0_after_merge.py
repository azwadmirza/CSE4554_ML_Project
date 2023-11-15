def present(name,
            value,
            record_type,
            dns_view,
            infoblox_server=None,
            infoblox_user=None,
            infoblox_password=None,
            infoblox_api_version='v1.4.2',
            sslVerify=True):
    '''
    Ensure a record exists

    name
        Name of the record

    value
        Value of the record

    record_type
        record type (host, a, cname, etc)

    dns_view
        DNS View

    infoblox_server
        infoblox server to connect to (will try pillar if not specified)

    infoblox_user
        username to use to connect to infoblox (will try pillar if not specified)

    infoblox_password
        password to use to connect to infoblox (will try pillar if not specified)

    verify_ssl
        verify SSL certificates

    Example:

    .. code-block:: yaml

        some-state:
            infoblox.present:
              - name: some.dns.record
              - value: 10.1.1.3
              - record_type: host
              - sslVerify: False
    '''
    record_type = record_type.lower()
    value_utf8 = six.text_type(value, "utf-8")
    ret = {'name': name, 'result': True, 'comment': '', 'changes': {}}
    records = __salt__['infoblox.get_record'](name,
                                              record_type,
                                              infoblox_server=infoblox_server,
                                              infoblox_user=infoblox_user,
                                              infoblox_password=infoblox_password,
                                              dns_view=dns_view,
                                              infoblox_api_version=infoblox_api_version,
                                              sslVerify=sslVerify)
    if records:
        # check records for updates
        for record in records:
            update_record = False
            if record_type == 'cname':
                if record['Canonical Name'] != value_utf8:
                    update_record = True
            elif record_type == 'a':
                if record['IP Address'] != value_utf8:
                    update_record = True
            elif record_type == 'host':
                if record['IP Addresses'] != [value_utf8]:
                    update_record = True
            if update_record:
                if __opts__['test']:
                    ret['result'] = None
                    ret['comment'] = ' '.join([ret['comment'],
                                     'DNS {0} record {1} in view {2} will be update'.format(record_type,
                                                                                            name,
                                                                                            dns_view)])
                else:
                    retval = __salt__['infoblox.update_record'](name,
                                                                value,
                                                                dns_view,
                                                                record_type,
                                                                infoblox_server=infoblox_server,
                                                                infoblox_user=infoblox_user,
                                                                infoblox_password=infoblox_password,
                                                                infoblox_api_version=infoblox_api_version,
                                                                sslVerify=sslVerify)
                    if retval:
                        if 'old' not in ret['changes']:
                            ret['changes']['old'] = []
                        if 'new' not in ret['changes']:
                            ret['changes']['new'] = []
                        ret['changes']['old'].append(record)
                        ret['changes']['new'].append(__salt__['infoblox.get_record'](name,
                                                                                     record_type,
                                                                                     infoblox_server=infoblox_server,
                                                                                     infoblox_user=infoblox_user,
                                                                                     infoblox_password=infoblox_password,
                                                                                     dns_view=dns_view,
                                                                                     infoblox_api_version=infoblox_api_version,
                                                                                     sslVerify=sslVerify))
                    else:
                        ret['result'] = False
                        return ret
    else:
        # no records
        if __opts__['test']:
            ret['result'] = None
            ret['comment'] = ' '.join([ret['comment'],
                             'DNS {0} record {1} set to be added to view {2}'.format(record_type,
                                                                                     name,
                                                                                     dns_view)])
            return ret
        retval = __salt__['infoblox.add_record'](name,
                                                 value,
                                                 record_type,
                                                 dns_view,
                                                 infoblox_server=infoblox_server,
                                                 infoblox_user=infoblox_user,
                                                 infoblox_password=infoblox_password,
                                                 infoblox_api_version='v1.4.2',
                                                 sslVerify=sslVerify)
        if retval:
            ret['result'] = True
            ret['changes']['old'] = None
            ret['changes']['new'] = __salt__['infoblox.get_record'](name,
                                                                    record_type,
                                                                    infoblox_server=infoblox_server,
                                                                    infoblox_user=infoblox_user,
                                                                    infoblox_password=infoblox_password,
                                                                    dns_view=dns_view,
                                                                    infoblox_api_version=infoblox_api_version,
                                                                    sslVerify=sslVerify)
    return ret