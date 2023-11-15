def info(*packages, **attr):
    '''
    Return a detailed package(s) summary information.
    If no packages specified, all packages will be returned.

    :param packages:

    :param attr:
        Comma-separated package attributes. If no 'attr' is specified, all available attributes returned.

        Valid attributes are:
            version, vendor, release, build_date, build_date_time_t, install_date, install_date_time_t,
            build_host, group, source_rpm, arch, epoch, size, license, signature, packager, url, summary, description.

    :return:

    CLI example:

    .. code-block:: bash

        salt '*' lowpkg.info apache2 bash
        salt '*' lowpkg.info apache2 bash attr=version
        salt '*' lowpkg.info apache2 bash attr=version,build_date_iso,size
    '''
    # LONGSIZE is not a valid tag for all versions of rpm. If LONGSIZE isn't
    # available, then we can just use SIZE for older versions. See Issue #31366.
    rpm_tags = __salt__['cmd.run_stdout'](
        ['rpm', '--querytags'],
        python_shell=False).splitlines()
    if 'LONGSIZE' in rpm_tags:
        size_tag = '%{LONGSIZE}'
    else:
        size_tag = '%{SIZE}'

    cmd = packages and "rpm -q {0}".format(' '.join(packages)) or "rpm -qa"

    # Construct query format
    attr_map = {
        "name": "name: %{NAME}\\n",
        "relocations": "relocations: %|PREFIXES?{[%{PREFIXES} ]}:{(not relocatable)}|\\n",
        "version": "version: %{VERSION}\\n",
        "vendor": "vendor: %{VENDOR}\\n",
        "release": "release: %{RELEASE}\\n",
        "epoch": "%|EPOCH?{epoch: %{EPOCH}\\n}|",
        "build_date_time_t": "build_date_time_t: %{BUILDTIME}\\n",
        "build_date": "build_date: %{BUILDTIME}\\n",
        "install_date_time_t": "install_date_time_t: %|INSTALLTIME?{%{INSTALLTIME}}:{(not installed)}|\\n",
        "install_date": "install_date: %|INSTALLTIME?{%{INSTALLTIME}}:{(not installed)}|\\n",
        "build_host": "build_host: %{BUILDHOST}\\n",
        "group": "group: %{GROUP}\\n",
        "source_rpm": "source_rpm: %{SOURCERPM}\\n",
        "size": "size: " + size_tag + "\\n",
        "arch": "arch: %{ARCH}\\n",
        "license": "%|LICENSE?{license: %{LICENSE}\\n}|",
        "signature": "signature: %|DSAHEADER?{%{DSAHEADER:pgpsig}}:{%|RSAHEADER?{%{RSAHEADER:pgpsig}}:"
                     "{%|SIGGPG?{%{SIGGPG:pgpsig}}:{%|SIGPGP?{%{SIGPGP:pgpsig}}:{(none)}|}|}|}|\\n",
        "packager": "%|PACKAGER?{packager: %{PACKAGER}\\n}|",
        "url": "%|URL?{url: %{URL}\\n}|",
        "summary": "summary: %{SUMMARY}\\n",
        "description": "description:\\n%{DESCRIPTION}\\n",
        "edition": "edition: %|EPOCH?{%{EPOCH}:}|%{VERSION}-%{RELEASE}\\n",
    }

    attr = attr.get('attr', None) and attr['attr'].split(",") or None
    query = list()
    if attr:
        for attr_k in attr:
            if attr_k in attr_map and attr_k != 'description':
                query.append(attr_map[attr_k])
        if not query:
            raise CommandExecutionError('No valid attributes found.')
        if 'name' not in attr:
            attr.append('name')
            query.append(attr_map['name'])
        if 'edition' not in attr:
            attr.append('edition')
            query.append(attr_map['edition'])
    else:
        for attr_k, attr_v in attr_map.iteritems():
            if attr_k != 'description':
                query.append(attr_v)
    if attr and 'description' in attr or not attr:
        query.append(attr_map['description'])
    query.append("-----\\n")

    call = __salt__['cmd.run_all'](cmd + (" --queryformat '{0}'".format(''.join(query))),
                                   output_loglevel='trace', env={'TZ': 'UTC'}, clean_env=True)
    if call['retcode'] != 0:
        comment = ''
        if 'stderr' in call:
            comment += (call['stderr'] or call['stdout'])
        raise CommandExecutionError('{0}'.format(comment))
    elif 'error' in call['stderr']:
        raise CommandExecutionError(call['stderr'])
    else:
        out = call['stdout']

    _ret = list()
    for pkg_info in re.split(r"----*", out):
        pkg_info = pkg_info.strip()
        if not pkg_info:
            continue
        pkg_info = pkg_info.split(os.linesep)
        if pkg_info[-1].lower().startswith('distribution'):
            pkg_info = pkg_info[:-1]

        pkg_data = dict()
        pkg_name = None
        descr_marker = False
        descr = list()
        for line in pkg_info:
            if descr_marker:
                descr.append(line)
                continue
            line = [item.strip() for item in line.split(':', 1)]
            if len(line) != 2:
                continue
            key, value = line
            if key == 'description':
                descr_marker = True
                continue
            if key == 'name':
                pkg_name = value

            # Convert Unix ticks into ISO time format
            if key in ['build_date', 'install_date']:
                try:
                    pkg_data[key] = datetime.datetime.fromtimestamp(int(value)).isoformat() + "Z"
                except ValueError:
                    log.warning('Could not convert "{0}" into Unix time'.format(value))
                continue

            # Convert Unix ticks into an Integer
            if key in ['build_date_time_t', 'install_date_time_t']:
                try:
                    pkg_data[key] = int(value)
                except ValueError:
                    log.warning('Could not convert "{0}" into Unix time'.format(value))
                continue
            if key not in ['description', 'name'] and value:
                pkg_data[key] = value
        if attr and 'description' in attr or not attr:
            pkg_data['description'] = os.linesep.join(descr)
        if pkg_name:
            pkg_data['name'] = pkg_name
            _ret.append(pkg_data)

    # Force-sort package data by version,
    # pick only latest versions
    # (in case multiple packages installed, e.g. kernel)
    ret = dict()
    for pkg_data in reversed(sorted(_ret, cmp=lambda a_vrs, b_vrs: version_cmp(a_vrs['edition'], b_vrs['edition']))):
        pkg_name = pkg_data.pop('name')
        if pkg_name not in ret:
            ret[pkg_name] = pkg_data.copy()
            del ret[pkg_name]['edition']

    return ret