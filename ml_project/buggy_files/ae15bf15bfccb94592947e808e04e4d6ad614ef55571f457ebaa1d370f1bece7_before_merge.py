def _freebsd_geom():
    geom = salt.utils.which('geom')
    ret = {'disks': {}, 'SSDs': []}

    devices = __salt__['cmd.run']('{0} disk list'.format(geom))
    devices = devices.split('\n\n')

    def parse_geom_attribs(device):
        tmp = {}
        for line in device.split('\n'):
            for attrib in _geom_attribs:
                search = re.search(r'{0}:\s(.*)'.format(attrib), line)
                if search:
                    value = _datavalue(_geomconsts._datatypes.get(attrib),
                                       search.group(1))
                    tmp[attrib] = value
                    if attrib in _geomconsts._aliases:
                        tmp[_geomconsts._aliases[attrib]] = value

        name = tmp.pop(_geomconsts.GEOMNAME)

        ret['disks'][name] = tmp
        if tmp[_geomconsts.ROTATIONRATE] == 0:
            log.trace('Device {0} reports itself as an SSD'.format(device))
            ret['SSDs'].append(name)

    for device in devices:
        parse_geom_attribs(device)

    return ret