def add_input_endpoint(kwargs=None, conn=None, call=None):
    '''
    .. versionadded:: 2015.8.0

    Add an input endpoint to the deployment. Please note that
    there may be a delay before the changes show up.

    CLI Example:

    .. code-block:: bash

        salt-cloud -f add_input_endpoint my-azure service=myservice \\
            deployment=mydeployment role=myrole name=HTTP local_port=80 \\
            port=80 protocol=tcp enable_direct_server_return=False \\
            timeout_for_tcp_idle_connection=4
    '''
    return update_input_endpoint(
        kwargs=kwargs,
        conn=conn,
        call='function',
        activity='add',
    )