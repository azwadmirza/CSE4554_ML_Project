def query(scope, **kwargs):
    '''
    Query the node for specific information.

    Parameters:

    * **scope**: Specify scope of the query.

       * **System**: Return system data.

       * **Software**: Return software information.

       * **Services**: Return known services.

       * **Identity**: Return user accounts information for this system.
          accounts
            Can be either 'local', 'remote' or 'all' (equal to "local,remote").
            Remote accounts cannot be resolved on all systems, but only
            those, which supports 'passwd -S -a'.

          disabled
            True (or False, default) to return only disabled accounts.

       * **payload**: Payload scope parameters:
          filter
            Include only results which path starts from the filter string.

          time
            Display time in Unix ticks or format according to the configured TZ (default)
            Values: ticks, tz (default)

          size
            Format size. Values: B, KB, MB, GB

          type
            Include payload type.
            Values (comma-separated): directory (or dir), link, file (default)
            Example (returns everything): type=directory,link,file

          owners
            Resolve UID/GID to an actual names or leave them numeric (default).
            Values: name (default), id

          brief
            Return just a list of payload elements, if True. Default: False.

       * **all**: Return all information (default).

    CLI Example:

    .. code-block:: bash

        salt '*' node.query scope=os
        salt '*' node.query payload type=file,link filter=/etc size=Kb brief=False
    '''
    query = _("query")
    try:
        return query.Query(scope)(**kwargs)
    except InspectorQueryException as ex:
        raise CommandExecutionError(ex)
    except Exception as ex:
        log.error(ex.message)
        raise Exception(ex)