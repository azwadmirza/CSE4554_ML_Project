def update_input_endpoint(kwargs=None, conn=None, call=None, activity='update'):
    '''
    .. versionadded:: 2015.8.0

    Update an input endpoint associated with the deployment. Please note that
    there may be a delay before the changes show up.

    CLI Example:

    .. code-block:: bash

        salt-cloud -f update_input_endpoint my-azure service=myservice \\
            deployment=mydeployment role=myrole name=HTTP local_port=80 \\
            port=80 protocol=tcp enable_direct_server_return=False \\
            timeout_for_tcp_idle_connection=4
    '''
    if call != 'function':
        raise SaltCloudSystemExit(
            'The update_input_endpoint function must be called with -f or --function.'
        )

    if kwargs is None:
        kwargs = {}

    if 'service' not in kwargs:
        raise SaltCloudSystemExit('A service name must be specified as "service"')

    if 'deployment' not in kwargs:
        raise SaltCloudSystemExit('A deployment name must be specified as "deployment"')

    if 'name' not in kwargs:
        raise SaltCloudSystemExit('An endpoint name must be specified as "name"')

    if 'role' not in kwargs:
        raise SaltCloudSystemExit('An role name must be specified as "role"')

    if activity != 'delete':
        if 'port' not in kwargs:
            raise SaltCloudSystemExit('An endpoint port must be specified as "port"')

        if 'protocol' not in kwargs:
            raise SaltCloudSystemExit('An endpoint protocol (tcp or udp) must be specified as "protocol"')

        if 'local_port' not in kwargs:
            kwargs['local_port'] = kwargs['port']

        if 'enable_direct_server_return' not in kwargs:
            kwargs['enable_direct_server_return'] = False
        kwargs['enable_direct_server_return'] = str(kwargs['enable_direct_server_return']).lower()

        if 'timeout_for_tcp_idle_connection' not in kwargs:
            kwargs['timeout_for_tcp_idle_connection'] = 4

    old_endpoints = list_input_endpoints(kwargs, call='function')

    endpoints_xml = ''
    endpoint_xml = '''
        <InputEndpoint>
          <LocalPort>{local_port}</LocalPort>
          <Name>{name}</Name>
          <Port>{port}</Port>
          <Protocol>{protocol}</Protocol>
          <EnableDirectServerReturn>{enable_direct_server_return}</EnableDirectServerReturn>
          <IdleTimeoutInMinutes>{timeout_for_tcp_idle_connection}</IdleTimeoutInMinutes>
        </InputEndpoint>'''

    if activity == 'add':
        old_endpoints[kwargs['name']] = kwargs
        old_endpoints[kwargs['name']]['Name'] = kwargs['name']

    for endpoint in old_endpoints:
        if old_endpoints[endpoint]['Name'] == kwargs['name']:
            if activity != 'delete':
                this_endpoint_xml = endpoint_xml.format(**kwargs)
                endpoints_xml += this_endpoint_xml
        else:
            this_endpoint_xml = endpoint_xml.format(
                local_port=old_endpoints[endpoint]['LocalPort'],
                name=old_endpoints[endpoint]['Name'],
                port=old_endpoints[endpoint]['Port'],
                protocol=old_endpoints[endpoint]['Protocol'],
                enable_direct_server_return=old_endpoints[endpoint]['EnableDirectServerReturn'],
                timeout_for_tcp_idle_connection=old_endpoints[endpoint].get('IdleTimeoutInMinutes', 4),
            )
            endpoints_xml += this_endpoint_xml

    request_xml = '''<PersistentVMRole xmlns="http://schemas.microsoft.com/windowsazure"
xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
  <ConfigurationSets>
    <ConfigurationSet>
      <ConfigurationSetType>NetworkConfiguration</ConfigurationSetType>
      <InputEndpoints>{0}
      </InputEndpoints>
    </ConfigurationSet>
  </ConfigurationSets>
  <OSVirtualHardDisk>
  </OSVirtualHardDisk>
</PersistentVMRole>'''.format(endpoints_xml)

    path = 'services/hostedservices/{0}/deployments/{1}/roles/{2}'.format(
        kwargs['service'],
        kwargs['deployment'],
        kwargs['role'],
    )
    query(
        path=path,
        method='PUT',
        header_dict={'Content-Type': 'application/xml'},
        data=request_xml,
        decode=False,
    )
    return True