def inspect(mode='all', priority=19, **kwargs):
    '''
    Start node inspection and save the data to the database for further query.

    Parameters:

    * **mode**: Clarify inspection mode: configuration, payload, all (default)

      payload
        * **filter**: Comma-separated directories to track payload.

    * **priority**: (advanced) Set priority of the inspection. Default is low priority.



    CLI Example:

    .. code-block:: bash

        salt '*' node.inspect
        salt '*' node.inspect configuration
        salt '*' node.inspect payload filter=/opt,/ext/oracle
    '''
    collector = _("collector")
    try:
        return collector.Inspector().request_snapshot(mode, priority=priority, **kwargs)
    except InspectorSnapshotException as ex:
        raise CommandExecutionError(ex)
    except Exception as ex:
        log.error(_get_error_message(ex))
        raise Exception(ex)