def create_network(
    name,
    skip_translate=None,
    ignore_collisions=False,
    validate_ip_addrs=True,
    client_timeout=salt.utils.docker.CLIENT_TIMEOUT,
    **kwargs
):
    """
    .. versionchanged:: 2018.3.0
        Support added for network configuration options other than ``driver``
        and ``driver_opts``, as well as IPAM configuration.

    Create a new network

    .. note::
        This function supports all arguments for network and IPAM pool
        configuration which are available for the release of docker-py
        installed on the minion. For that reason, the arguments described below
        in the :ref:`NETWORK CONFIGURATION ARGUMENTS
        <salt-modules-dockermod-create-network-netconf>` and :ref:`IP ADDRESS
        MANAGEMENT (IPAM) <salt-modules-dockermod-create-network-ipam>`
        sections may not accurately reflect what is available on the minion.
        The :py:func:`docker.get_client_args
        <salt.modules.dockermod.get_client_args>` function can be used to check
        the available arguments for the installed version of docker-py (they
        are found in the ``network_config`` and ``ipam_config`` sections of the
        return data), but Salt will not prevent a user from attempting to use
        an argument which is unsupported in the release of Docker which is
        installed. In those cases, network creation be attempted but will fail.

    name
        Network name

    skip_translate
        This function translates Salt CLI or SLS input into the format which
        docker-py expects. However, in the event that Salt's translation logic
        fails (due to potential changes in the Docker Remote API, or to bugs in
        the translation code), this argument can be used to exert granular
        control over which arguments are translated and which are not.

        Pass this argument as a comma-separated list (or Python list) of
        arguments, and translation for each passed argument name will be
        skipped. Alternatively, pass ``True`` and *all* translation will be
        skipped.

        Skipping tranlsation allows for arguments to be formatted directly in
        the format which docker-py expects. This allows for API changes and
        other issues to be more easily worked around. See the following links
        for more information:

        - `docker-py Low-level API`_
        - `Docker Engine API`_

        .. versionadded:: 2018.3.0

    ignore_collisions : False
        Since many of docker-py's arguments differ in name from their CLI
        counterparts (with which most Docker users are more familiar), Salt
        detects usage of these and aliases them to the docker-py version of
        that argument. However, if both the alias and the docker-py version of
        the same argument (e.g. ``options`` and ``driver_opts``) are used, an error
        will be raised. Set this argument to ``True`` to suppress these errors
        and keep the docker-py version of the argument.

        .. versionadded:: 2018.3.0

    validate_ip_addrs : True
        For parameters which accept IP addresses as input, IP address
        validation will be performed. To disable, set this to ``False``

        .. note::
            When validating subnets, whether or not the IP portion of the
            subnet is a valid subnet boundary will not be checked. The IP will
            portion will be validated, and the subnet size will be checked to
            confirm it is a valid number (1-32 for IPv4, 1-128 for IPv6).

        .. versionadded:: 2018.3.0

    .. _salt-modules-dockermod-create-network-netconf:

    **NETWORK CONFIGURATION ARGUMENTS**

    driver
        Network driver

        Example: ``driver=macvlan``

    driver_opts (or *driver_opt*, or *options*)
        Options for the network driver. Either a dictionary of option names and
        values or a Python list of strings in the format ``varname=value``.

        Examples:

        - ``driver_opts='macvlan_mode=bridge,parent=eth0'``
        - ``driver_opts="['macvlan_mode=bridge', 'parent=eth0']"``
        - ``driver_opts="{'macvlan_mode': 'bridge', 'parent': 'eth0'}"``

    check_duplicate : True
        If ``True``, checks for networks with duplicate names. Since networks
        are primarily keyed based on a random ID and not on the name, and
        network name is strictly a user-friendly alias to the network which is
        uniquely identified using ID, there is no guaranteed way to check for
        duplicates. This option providess a best effort, checking for any
        networks which have the same name, but it is not guaranteed to catch
        all name collisions.

        Example: ``check_duplicate=False``

    internal : False
        If ``True``, restricts external access to the network

        Example: ``internal=True``

    labels
        Add metadata to the network. Labels can be set both with and without
        values:

        Examples (*with* values):

        - ``labels="label1=value1,label2=value2"``
        - ``labels="['label1=value1', 'label2=value2']"``
        - ``labels="{'label1': 'value1', 'label2': 'value2'}"``

        Examples (*without* values):

        - ``labels=label1,label2``
        - ``labels="['label1', 'label2']"``

    enable_ipv6 (or *ipv6*) : False
        Enable IPv6 on the network

        Example: ``enable_ipv6=True``

        .. note::
            While it should go without saying, this argument must be set to
            ``True`` to :ref:`configure an IPv6 subnet
            <salt-states-docker-network-present-ipam>`. Also, if this option is
            turned on without an IPv6 subnet explicitly configured, you will
            get an error unless you have set up a fixed IPv6 subnet. Consult
            the `Docker IPv6 docs`_ for information on how to do this.

            .. _`Docker IPv6 docs`: https://docs.docker.com/v17.09/engine/userguide/networking/default_network/ipv6/

    attachable : False
        If ``True``, and the network is in the global scope, non-service
        containers on worker nodes will be able to connect to the network.

        Example: ``attachable=True``

        .. note::
            While support for this option was added in API version 1.24, its
            value was not added to the inpsect results until API version 1.26.
            The version of Docker which is available for CentOS 7 runs API
            version 1.24, meaning that while Salt can pass this argument to the
            API, it has no way of knowing the value of this config option in an
            existing Docker network.

    scope
        Specify the network's scope (``local``, ``global`` or ``swarm``)

        Example: ``scope=local``

    ingress : False
        If ``True``, create an ingress network which provides the routing-mesh in
        swarm mode

        Example: ``ingress=True``

    .. _salt-modules-dockermod-create-network-ipam:

    **IP ADDRESS MANAGEMENT (IPAM)**

    This function supports networks with either IPv4, or both IPv4 and IPv6. If
    configuring IPv4, then you can pass the IPAM arguments as shown below, as
    individual arguments on the Salt CLI. However, if configuring IPv4 and
    IPv6, the arguments must be passed as a list of dictionaries, in the
    ``ipam_pools`` argument. See the **CLI Examples** below. `These docs`_ also
    have more information on these arguments.

    .. _`These docs`: http://docker-py.readthedocs.io/en/stable/api.html#docker.types.IPAMPool

    *IPAM ARGUMENTS*

    ipam_driver
        IPAM driver to use, if different from the default one

        Example: ``ipam_driver=foo``

    ipam_opts
        Options for the IPAM driver. Either a dictionary of option names
        and values or a Python list of strings in the format
        ``varname=value``.

        Examples:

        - ``ipam_opts='foo=bar,baz=qux'``
        - ``ipam_opts="['foo=bar', 'baz=quz']"``
        - ``ipam_opts="{'foo': 'bar', 'baz': 'qux'}"``

    *IPAM POOL ARGUMENTS*

    subnet
        Subnet in CIDR format that represents a network segment

        Example: ``subnet=192.168.50.0/25``

    iprange (or *ip_range*)
        Allocate container IP from a sub-range within the subnet

        Subnet in CIDR format that represents a network segment

        Example: ``iprange=192.168.50.64/26``

    gateway
        IPv4 gateway for the master subnet

        Example: ``gateway=192.168.50.1``

    aux_addresses (or *aux_address*)
        A dictionary of mapping container names to IP addresses which should be
        allocated for them should they connect to the network. Either a
        dictionary of option names and values or a Python list of strings in
        the format ``host=ipaddr``.

        Examples:

        - ``aux_addresses='foo.bar.tld=192.168.50.10,hello.world.tld=192.168.50.11'``
        - ``aux_addresses="['foo.bar.tld=192.168.50.10', 'hello.world.tld=192.168.50.11']"``
        - ``aux_addresses="{'foo.bar.tld': '192.168.50.10', 'hello.world.tld': '192.168.50.11'}"``


    CLI Examples:

    .. code-block:: bash

        salt myminion docker.create_network web_network driver=bridge
        # IPv4
        salt myminion docker.create_network macvlan_network driver=macvlan driver_opts="{'parent':'eth0'}" gateway=172.20.0.1 subnet=172.20.0.0/24
        # IPv4 and IPv6
        salt myminion docker.create_network mynet ipam_pools='[{"subnet": "10.0.0.0/24", "gateway": "10.0.0.1"}, {"subnet": "fe3f:2180:26:1::60/123", "gateway": "fe3f:2180:26:1::61"}]'
    """
    kwargs = __utils__["docker.translate_input"](
        salt.utils.docker.translate.network,
        skip_translate=skip_translate,
        ignore_collisions=ignore_collisions,
        validate_ip_addrs=validate_ip_addrs,
        **__utils__["args.clean_kwargs"](**kwargs)
    )

    if "ipam" not in kwargs:
        ipam_kwargs = {}
        for key in [
            x
            for x in ["ipam_driver", "ipam_opts"]
            + get_client_args("ipam_config")["ipam_config"]
            if x in kwargs
        ]:
            ipam_kwargs[key] = kwargs.pop(key)
        ipam_pools = kwargs.pop("ipam_pools", ())

        # Don't go through the work of building a config dict if no
        # IPAM-specific configuration was passed. Just create the network
        # without specifying IPAM configuration.
        if ipam_pools or ipam_kwargs:
            kwargs["ipam"] = __utils__["docker.create_ipam_config"](
                *ipam_pools, **ipam_kwargs
            )

    response = _client_wrapper("create_network", name, **kwargs)
    _clear_context()
    # Only non-error return case is a True return, so just return the response
    return response