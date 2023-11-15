def get_service_instance(
    host,
    username=None,
    password=None,
    protocol=None,
    port=None,
    mechanism="userpass",
    principal=None,
    domain=None,
):
    """
    Authenticate with a vCenter server or ESX/ESXi host and return the service instance object.

    host
        The location of the vCenter server or ESX/ESXi host.

    username
        The username used to login to the vCenter server or ESX/ESXi host.
        Required if mechanism is ``userpass``

    password
        The password used to login to the vCenter server or ESX/ESXi host.
        Required if mechanism is ``userpass``

    protocol
        Optionally set to alternate protocol if the vCenter server or ESX/ESXi host is not
        using the default protocol. Default protocol is ``https``.

    port
        Optionally set to alternate port if the vCenter server or ESX/ESXi host is not
        using the default port. Default port is ``443``.

    mechanism
        pyVmomi connection mechanism. Can either be ``userpass`` or ``sspi``.
        Default mechanism is ``userpass``.

    principal
        Kerberos service principal. Required if mechanism is ``sspi``

    domain
        Kerberos user domain. Required if mechanism is ``sspi``
    """

    if protocol is None:
        protocol = "https"
    if port is None:
        port = 443

    service_instance = GetSi()
    if service_instance:
        stub = GetStub()
        if salt.utils.platform.is_proxy() or (
            hasattr(stub, "host") and stub.host != ":".join([host, str(port)])
        ):
            # Proxies will fork and mess up the cached service instance.
            # If this is a proxy or we are connecting to a different host
            # invalidate the service instance to avoid a potential memory leak
            # and reconnect
            Disconnect(service_instance)
            service_instance = None

    if not service_instance:
        service_instance = _get_service_instance(
            host, username, password, protocol, port, mechanism, principal, domain
        )

    # Test if data can actually be retrieved or connection has gone stale
    log.trace("Checking connection is still authenticated")
    try:
        service_instance.CurrentTime()
    except vim.fault.NotAuthenticated:
        log.trace("Session no longer authenticating. Reconnecting")
        Disconnect(service_instance)
        service_instance = _get_service_instance(
            host, username, password, protocol, port, mechanism, principal, domain
        )
    except vim.fault.NoPermission as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(
            "Not enough permissions. Required privilege: " "{}".format(exc.privilegeId)
        )
    except vim.fault.VimFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareApiError(exc.msg)
    except vmodl.RuntimeFault as exc:
        log.exception(exc)
        raise salt.exceptions.VMwareRuntimeError(exc.msg)

    return service_instance