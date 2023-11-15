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
        if name.startswith('cd'):
            return

        ret['disks'][name] = tmp
        if tmp[_geomconsts.ROTATIONRATE] == 0:
            log.trace('Device {0} reports itself as an SSD'.format(device))
            ret['SSDs'].append(name)