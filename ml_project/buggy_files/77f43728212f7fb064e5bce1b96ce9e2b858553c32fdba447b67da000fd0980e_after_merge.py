def build_interface(iface, iface_type, enabled, **settings):
    '''
    Build an interface script for a network interface.

    CLI Example:

    .. code-block:: bash

        salt '*' ip.build_interface eth0 eth <settings>
    '''
    if __grains__['os'] == 'Fedora':
        rh_major = '6'
    else:
        rh_major = __grains__['osrelease'][:1]

    iface = iface.lower()
    iface_type = iface_type.lower()

    if iface_type not in _IFACE_TYPES:
        _raise_error_iface(iface, iface_type, _IFACE_TYPES)

    if iface_type == 'slave':
        settings['slave'] = 'yes'
        if 'master' not in settings:
            msg = 'master is a required setting for slave interfaces'
            log.error(msg)
            raise AttributeError(msg)

    if iface_type == 'vlan':
        settings['vlan'] = 'yes'

    if iface_type == 'bridge':
        __salt__['pkg.install']('bridge-utils')

    if iface_type in ['eth', 'bond', 'bridge', 'slave', 'vlan', 'ipip', 'ib', 'alias']:
        opts = _parse_settings_eth(settings, iface_type, enabled, iface)
        try:
            template = JINJA.get_template('rh{0}_eth.jinja'.format(rh_major))
        except jinja2.exceptions.TemplateNotFound:
            log.error(
                'Could not load template rh{0}_eth.jinja'.format(
                    rh_major
                )
            )
            return ''
        ifcfg = template.render(opts)

    if 'test' in settings and settings['test']:
        return _read_temp(ifcfg)

    _write_file_iface(iface, ifcfg, _RH_NETWORK_SCRIPT_DIR, 'ifcfg-{0}')
    path = os.path.join(_RH_NETWORK_SCRIPT_DIR, 'ifcfg-{0}'.format(iface))

    return _read_file(path)