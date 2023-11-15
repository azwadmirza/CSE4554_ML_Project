def _read_nmap_probes():
    global _NMAP_CUR_PROBE, _NMAP_PROBES_POPULATED
    _NMAP_CUR_PROBE = None
    def parse_line(line):
        global _NMAP_PROBES, _NMAP_CUR_PROBE
        if line.startswith(b'match '):
            line = line[6:]
            soft = False
        elif line.startswith(b'softmatch '):
            line = line[10:]
            soft = True
        elif line.startswith(b'Probe '):
            _NMAP_CUR_PROBE = []
            proto, name, probe = line[6:].split(b' ', 2)
            _NMAP_PROBES.setdefault(proto.lower().decode(),
                                    {})[name.decode()] = {
                "probe": probe, "fp": _NMAP_CUR_PROBE
            }
            return
        else:
            return
        service, data = line.split(b' ', 1)
        info = {"soft": soft}
        while data:
            if data.startswith(b'cpe:'):
                key = 'cpe'
                data = data[4:]
            else:
                key = data[0:1].decode()
                data = data[1:]
            sep = data[0:1]
            data = data[1:]
            index = data.index(sep)
            value = data[:index]
            data = data[index + 1:]
            flag = b''
            if data:
                if b' ' in data:
                    flag, data = data.split(b' ', 1)
                else:
                    flag, data = data, b''
            if key == 'm':
                if value.endswith(b'\\r\\n'):
                    value = value[:-4] + b'(?:\\r\\n|$)'
                elif value.endswith(b'\\\\n'):
                    value = value[:3] + b'(?:\\\\n|$)'
                elif value.endswith(b'\\n'):
                    value = value[:-2] + b'(?:\\n|$)'
                value = re.compile(
                    value,
                    flags=sum(getattr(re, f) if hasattr(re, f) else 0
                              for f in flag.decode().upper()),
                )
                flag = b''
            else:
                value = value.decode()
            info[key] = (value, flag)
        _NMAP_CUR_PROBE.append((service.decode(), info))
    try:
        with open(os.path.join(config.NMAP_SHARE_PATH, 'nmap-service-probes'),
                  'rb') as fdesc:
            for line in fdesc:
                parse_line(line[:-1])
    except (AttributeError, TypeError, IOError):
        LOGGER.warning('Cannot read Nmap service fingerprint file.',
                       exc_info=True)
    del _NMAP_CUR_PROBE
    _NMAP_PROBES_POPULATED = True