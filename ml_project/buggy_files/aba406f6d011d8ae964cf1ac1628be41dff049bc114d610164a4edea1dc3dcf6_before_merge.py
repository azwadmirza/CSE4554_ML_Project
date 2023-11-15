def get_local_client(
        c_path=os.path.join(syspaths.CONFIG_DIR, 'master'),
        mopts=None,
        skip_perm_errors=False,
        io_loop=None):
    '''
    .. versionadded:: 2014.7.0

    Read in the config and return the correct LocalClient object based on
    the configured transport

    :param IOLoop io_loop: io_loop used for events.
                           Pass in an io_loop if you want asynchronous
                           operation for obtaining events. Eg use of
                           set_event_handler() API. Otherwise, operation
                           will be synchronous.
    '''
    if mopts:
        opts = mopts
    else:
        # Late import to prevent circular import
        import salt.config
        opts = salt.config.client_config(c_path)
    if opts['transport'] == 'raet':
        import salt.client.raet
        return salt.client.raet.LocalClient(mopts=opts)
    # TODO: AIO core is separate from transport
    elif opts['transport'] in ('zeromq', 'tcp'):
        return LocalClient(
            mopts=opts,
            skip_perm_errors=skip_perm_errors,
            io_loop=io_loop)