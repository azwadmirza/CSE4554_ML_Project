def _get_pkg_info(*packages):
    '''
    Return list of package informations. If 'packages' parameter is empty,
    then data about all installed packages will be returned.

    :param packages: Specified packages.
    :return:
    '''

    if __grains__['os'] == 'Ubuntu' and __grains__['osrelease_info'] <= (12, 4):
        bin_var = '${binary}'
    else:
        bin_var = '${binary:Package}'

    ret = []
    cmd = "dpkg-query -W -f='package:" + bin_var + "\\n" \
          "revision:${binary:Revision}\\n" \
          "architecture:${Architecture}\\n" \
          "maintainer:${Maintainer}\\n" \
          "summary:${Summary}\\n" \
          "source:${source:Package}\\n" \
          "version:${Version}\\n" \
          "section:${Section}\\n" \
          "installed_size:${Installed-size}\\n" \
          "size:${Size}\\n" \
          "MD5:${MD5sum}\\n" \
          "SHA1:${SHA1}\\n" \
          "SHA256:${SHA256}\\n" \
          "origin:${Origin}\\n" \
          "homepage:${Homepage}\\n" \
          "======\\n" \
          "description:${Description}\\n" \
          "------\\n'"
    cmd += ' {0}'.format(' '.join(packages))
    cmd = cmd.strip()

    call = __salt__['cmd.run_all'](cmd, python_chell=False)
    if call['retcode']:
        raise CommandExecutionError("Error getting packages information: {0}".format(call['stderr']))

    for pkg_info in [elm for elm in re.split(r"----*", call['stdout']) if elm.strip()]:
        pkg_data = {}
        pkg_info, pkg_descr = re.split(r"====*", pkg_info)
        for pkg_info_line in [el.strip() for el in pkg_info.split(os.linesep) if el.strip()]:
            key, value = pkg_info_line.split(":", 1)
            if value:
                pkg_data[key] = value
            install_date = _get_pkg_install_time(pkg_data.get('package'))
            if install_date:
                pkg_data['install_date'] = install_date
        pkg_data['description'] = pkg_descr.split(":", 1)[-1]
        ret.append(pkg_data)

    return ret