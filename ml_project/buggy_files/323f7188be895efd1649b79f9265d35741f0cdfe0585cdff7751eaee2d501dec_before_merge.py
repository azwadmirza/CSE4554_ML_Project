def api(server, command, *args, **kwargs):
    """
    Call the Spacewalk xmlrpc api.

    CLI Example:

    .. code-block:: bash

        salt-run spacewalk.api spacewalk01.domain.com systemgroup.create MyGroup Description
        salt-run spacewalk.api spacewalk01.domain.com systemgroup.create arguments='["MyGroup", "Description"]'

    State Example:

    .. code-block:: yaml

        create_group:
          salt.runner:
            - name: spacewalk.api
            - server: spacewalk01.domain.com
            - command: systemgroup.create
            - arguments:
              - MyGroup
              - Description
    """
    if "arguments" in kwargs:
        arguments = kwargs["arguments"]
    else:
        arguments = args

    call = "{} {}".format(command, arguments)
    try:
        client, key = _get_session(server)
    except Exception as exc:  # pylint: disable=broad-except
        err_msg = "Exception raised when connecting to spacewalk server ({}): {}".format(
            server, exc
        )
        log.error(err_msg)
        return {call: err_msg}

    namespace, method = command.split(".")
    endpoint = getattr(getattr(client, namespace), method)

    try:
        output = endpoint(key, *arguments)
    except Exception as e:  # pylint: disable=broad-except
        output = "API call failed: {}".format(e)

    return {call: output}