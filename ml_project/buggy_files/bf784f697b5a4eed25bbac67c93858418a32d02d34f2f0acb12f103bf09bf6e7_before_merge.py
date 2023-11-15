def _network_conf(conf_tuples=None, **kwargs):
    '''
    Network configuration defaults

        network_profile
            as for containers, we can either call this function
            either with a network_profile dict or network profile name
            in the kwargs
        nic_opts
            overrides or extra nics in the form {nic_name: {set: tings}

    '''
    nic = kwargs.get('network_profile', None)
    ret = []
    nic_opts = kwargs.get('nic_opts', {})
    if nic_opts is None:
        # coming from elsewhere
        nic_opts = {}
    if not conf_tuples:
        conf_tuples = []
    old = _get_veths(conf_tuples)
    if not old:
        old = {}

    # if we have a profile name, get the profile and load the network settings
    # this will obviously by default  look for a profile called "eth0"
    # or by what is defined in nic_opts
    # and complete each nic settings by sane defaults
    if nic and isinstance(nic, (six.string_types, dict)):
        nicp = get_network_profile(nic)
    else:
        nicp = {}
    if DEFAULT_NIC not in nicp:
        nicp[DEFAULT_NIC] = {}

    kwargs = copy.deepcopy(kwargs)
    gateway = kwargs.pop('gateway', None)
    bridge = kwargs.get('bridge', None)
    if nic_opts:
        for dev, args in six.iteritems(nic_opts):
            ethx = nicp.setdefault(dev, {})
            try:
                ethx = salt.utils.dictupdate.update(ethx, args)
            except AttributeError:
                raise SaltInvocationError('Invalid nic_opts configuration')
    ifs = [a for a in nicp]
    ifs += [a for a in old if a not in nicp]
    ifs.sort()
    gateway_set = False
    for dev in ifs:
        args = nicp.get(dev, {})
        opts = nic_opts.get(dev, {}) if nic_opts else {}
        old_if = old.get(dev, {})
        disable = opts.get('disable', args.get('disable', False))
        if disable:
            continue
        mac = opts.get('mac',
                       opts.get('hwaddr',
                                args.get('mac',
                                         args.get('hwaddr', ''))))
        type_ = opts.get('type', args.get('type', ''))
        flags = opts.get('flags', args.get('flags', ''))
        link = opts.get('link', args.get('link', ''))
        ipv4 = opts.get('ipv4', args.get('ipv4', ''))
        ipv6 = opts.get('ipv6', args.get('ipv6', ''))
        infos = salt.utils.odict.OrderedDict([
            ('lxc.network.type', {
                'test': not type_,
                'value': type_,
                'old': old_if.get('lxc.network.type'),
                'default': 'veth'}),
            ('lxc.network.name', {
                'test': False,
                'value': dev,
                'old': dev,
                'default': dev}),
            ('lxc.network.flags', {
                'test': not flags,
                'value': flags,
                'old': old_if.get('lxc.network.flags'),
                'default': 'up'}),
            ('lxc.network.link', {
                'test': not link,
                'value': link,
                'old': old_if.get('lxc.network.link'),
                'default': search_lxc_bridge()}),
            ('lxc.network.hwaddr', {
                'test': not mac,
                'value': mac,
                'old': old_if.get('lxc.network.hwaddr'),
                'default': salt.utils.network.gen_mac()}),
            ('lxc.network.ipv4', {
                'test': not ipv4,
                'value': ipv4,
                'old': old_if.get('lxc.network.ipv4', ''),
                'default': None}),
            ('lxc.network.ipv6', {
                'test': not ipv6,
                'value': ipv6,
                'old': old_if.get('lxc.network.ipv6', ''),
                'default': None})])
        # for each parameter, if not explicitly set, the
        # config value present in the LXC configuration should
        # take precedence over the profile configuration
        for info in list(infos.keys()):
            bundle = infos[info]
            if bundle['test']:
                if bundle['old']:
                    bundle['value'] = bundle['old']
                elif bundle['default']:
                    bundle['value'] = bundle['default']
        for info, data in six.iteritems(infos):
            if data['value']:
                ret.append({info: data['value']})
        for key, val in six.iteritems(args):
            if key == 'link' and bridge:
                val = bridge
            val = opts.get(key, val)
            if key in [
                'type', 'flags', 'name',
                'gateway', 'mac', 'link', 'ipv4', 'ipv6'
            ]:
                continue
            ret.append({'lxc.network.{0}'.format(key): val})
        # gateway (in automode) must be appended following network conf !
        if not gateway:
            gateway = args.get('gateway', None)
        if gateway is not None and not gateway_set:
            ret.append({'lxc.network.ipv4.gateway': gateway})
            # only one network gateway ;)
            gateway_set = True
    # normally, this won't happen
    # set the gateway if specified even if we did
    # not managed the network underlying
    if gateway is not None and not gateway_set:
        ret.append({'lxc.network.ipv4.gateway': gateway})
        # only one network gateway ;)
        gateway_set = True

    new = _get_veths(ret)
    # verify that we did not loose the mac settings
    for iface in [a for a in new]:
        ndata = new[iface]
        nmac = ndata.get('lxc.network.hwaddr', '')
        ntype = ndata.get('lxc.network.type', '')
        omac, otype = '', ''
        if iface in old:
            odata = old[iface]
            omac = odata.get('lxc.network.hwaddr', '')
            otype = odata.get('lxc.network.type', '')
        # default for network type is setted here
        # attention not to change the network type
        # without a good and explicit reason to.
        if otype and not ntype:
            ntype = otype
        if not ntype:
            ntype = 'veth'
        new[iface]['lxc.network.type'] = ntype
        if omac and not nmac:
            new[iface]['lxc.network.hwaddr'] = omac

    ret = []
    for val in six.itervalues(new):
        for row in val:
            ret.append(salt.utils.odict.OrderedDict([(row, val[row])]))
    # on old versions of lxc, still support the gateway auto mode
    # if we didn't explicitly say no to
    # (lxc.network.ipv4.gateway: auto)
    if _LooseVersion(version()) <= '1.0.7' and \
            True not in ['lxc.network.ipv4.gateway' in a for a in ret] and \
            True in ['lxc.network.ipv4' in a for a in ret]:
        ret.append({'lxc.network.ipv4.gateway': 'auto'})
    return ret