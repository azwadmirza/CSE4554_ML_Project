def _list_certs(certificate_store='My'):
    '''
    List details of available certificates in the LocalMachine certificate
    store.

    Args:
        certificate_store (str): The name of the certificate store on the local
            machine.

    Returns:
        dict: A dictionary of certificates found in the store
    '''
    ret = dict()
    blacklist_keys = ['DnsNameList', 'Thumbprint']

    ps_cmd = ['Get-ChildItem',
              '-Path', r"'Cert:\LocalMachine\{0}'".format(certificate_store),
              '|',
              'Select-Object DnsNameList, SerialNumber, Subject, Thumbprint, Version']

    cmd_ret = _srvmgr(cmd=ps_cmd, return_json=True)

    try:
        items = salt.utils.json.loads(cmd_ret['stdout'], strict=False)
    except ValueError:
        raise CommandExecutionError('Unable to parse return data as Json.')

    for item in items:

        cert_info = dict()
        for key in item:
            if key not in blacklist_keys:
                cert_info[key.lower()] = item[key]

        cert_info['dnsnames'] = [name['Unicode'] for name in item['DnsNameList']]
        ret[item['Thumbprint']] = cert_info

    return ret