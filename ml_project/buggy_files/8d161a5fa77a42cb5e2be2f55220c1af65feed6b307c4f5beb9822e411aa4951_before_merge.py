def delete_input_endpoint(kwargs=None, conn=None, call=None):
    '''
    .. versionadded:: 2015.8.0

    Delete an input endpoint from the deployment. Please note that
    there may be a delay before the changes show up.

    CLI Example:

    .. code-block:: bash

        salt-cloud -f delete_input_endpoint my-azure service=myservice \
            deployment=mydeployment role=myrole name=HTTP
    '''
    return update_input_endpoint(
        kwargs=kwargs,
        conn=conn,
        call='function',
        activity='delete',
    )