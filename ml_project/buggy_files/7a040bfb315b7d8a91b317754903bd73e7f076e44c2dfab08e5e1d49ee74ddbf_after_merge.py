def create(
    image,
    name=None,
    start=False,
    skip_translate=None,
    ignore_collisions=False,
    validate_ip_addrs=True,
    client_timeout=salt.utils.dockermod.CLIENT_TIMEOUT,
    **kwargs
):
    """
    Create a new container

    image
        Image from which to create the container

    name
        Name for the new container. If not provided, Docker will randomly
        generate one for you (it will be included in the return data).

    start : False
        If ``True``, start container after creating it

        .. versionadded:: 2018.3.0

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
        other issues to be more easily worked around. An example of using this
        option to skip translation would be:

        .. code-block:: bash

            salt myminion docker.create image=centos:7.3.1611 skip_translate=environment environment="{'FOO': 'bar'}"

        See the following links for more information:

        - `docker-py Low-level API`_
        - `Docker Engine API`_

    ignore_collisions : False
        Since many of docker-py's arguments differ in name from their CLI
        counterparts (with which most Docker users are more familiar), Salt
        detects usage of these and aliases them to the docker-py version of
        that argument. However, if both the alias and the docker-py version of
        the same argument (e.g. ``env`` and ``environment``) are used, an error
        will be raised. Set this argument to ``True`` to suppress these errors
        and keep the docker-py version of the argument.

    validate_ip_addrs : True
        For parameters which accept IP addresses as input, IP address
        validation will be performed. To disable, set this to ``False``

    client_timeout : 60
        Timeout in seconds for the Docker client. This is not a timeout for
        this function, but for receiving a response from the API.

        .. note::

            This is only used if Salt needs to pull the requested image.

    **CONTAINER CONFIGURATION ARGUMENTS**

    auto_remove (or *rm*) : False
        Enable auto-removal of the container on daemon side when the
        container’s process exits (analogous to running a docker container with
        ``--rm`` on the CLI).

        Examples:

        - ``auto_remove=True``
        - ``rm=True``

    binds
        Files/directories to bind mount. Each bind mount should be passed in
        one of the following formats:

        - ``<host_path>:<container_path>`` - ``host_path`` is mounted within
          the container as ``container_path`` with read-write access.
        - ``<host_path>:<container_path>:<selinux_context>`` - ``host_path`` is
          mounted within the container as ``container_path`` with read-write
          access. Additionally, the specified selinux context will be set
          within the container.
        - ``<host_path>:<container_path>:<read_only>`` - ``host_path`` is
          mounted within the container as ``container_path``, with the
          read-only or read-write setting explicitly defined.
        - ``<host_path>:<container_path>:<read_only>,<selinux_context>`` -
          ``host_path`` is mounted within the container as ``container_path``,
          with the read-only or read-write setting explicitly defined.
          Additionally, the specified selinux context will be set within the
          container.

        ``<read_only>`` can be either ``ro`` for read-write access, or ``ro``
        for read-only access. When omitted, it is assumed to be read-write.

        ``<selinux_context>`` can be ``z`` if the volume is shared between
        multiple containers, or ``Z`` if the volume should be private.

        .. note::
            When both ``<read_only>`` and ``<selinux_context>`` are specified,
            there must be a comma before ``<selinux_context>``.

        Binds can be expressed as a comma-separated list or a Python list,
        however in cases where both ro/rw and an selinux context are specified,
        the binds *must* be specified as a Python list.

        Examples:

        - ``binds=/srv/www:/var/www:ro``
        - ``binds=/srv/www:/var/www:rw``
        - ``binds=/srv/www:/var/www``
        - ``binds="['/srv/www:/var/www:ro,Z']"``
        - ``binds="['/srv/www:/var/www:rw,Z']"``
        - ``binds=/srv/www:/var/www:Z``

        .. note::
            The second and third examples above are equivalent to each other,
            as are the last two examples.

    blkio_weight
        Block IO weight (relative weight), accepts a weight value between 10
        and 1000.

        Example: ``blkio_weight=100``

    blkio_weight_device
        Block IO weight (relative device weight), specified as a list of
        expressions in the format ``PATH:WEIGHT``

        Example: ``blkio_weight_device=/dev/sda:100``

    cap_add
        List of capabilities to add within the container. Can be passed as a
        comma-separated list or a Python list. Requires Docker 1.2.0 or
        newer.

        Examples:

        - ``cap_add=SYS_ADMIN,MKNOD``
        - ``cap_add="[SYS_ADMIN, MKNOD]"``

    cap_drop
        List of capabilities to drop within the container. Can be passed as a
        comma-separated string or a Python list. Requires Docker 1.2.0 or
        newer.

        Examples:

        - ``cap_drop=SYS_ADMIN,MKNOD``,
        - ``cap_drop="[SYS_ADMIN, MKNOD]"``

    command (or *cmd*)
        Command to run in the container

        Example: ``command=bash`` or ``cmd=bash``

        .. versionchanged:: 2015.8.1
            ``cmd`` is now also accepted

    cpuset_cpus (or *cpuset*)
        CPUs on which which to allow execution, specified as a string
        containing a range (e.g. ``0-3``) or a comma-separated list of CPUs
        (e.g. ``0,1``).

        Examples:

        - ``cpuset_cpus="0-3"``
        - ``cpuset="0,1"``

    cpuset_mems
        Memory nodes on which which to allow execution, specified as a string
        containing a range (e.g. ``0-3``) or a comma-separated list of MEMs
        (e.g. ``0,1``). Only effective on NUMA systems.

        Examples:

        - ``cpuset_mems="0-3"``
        - ``cpuset_mems="0,1"``

    cpu_group
        The length of a CPU period in microseconds

        Example: ``cpu_group=100000``

    cpu_period
        Microseconds of CPU time that the container can get in a CPU period

        Example: ``cpu_period=50000``

    cpu_shares
        CPU shares (relative weight), specified as an integer between 2 and 1024.

        Example: ``cpu_shares=512``

    detach : False
        If ``True``, run the container's command in the background (daemon
        mode)

        Example: ``detach=True``

    devices
        List of host devices to expose within the container

        Examples:

        - ``devices="/dev/net/tun,/dev/xvda1:/dev/xvda1,/dev/xvdb1:/dev/xvdb1:r"``
        - ``devices="['/dev/net/tun', '/dev/xvda1:/dev/xvda1', '/dev/xvdb1:/dev/xvdb1:r']"``

    device_read_bps
        Limit read rate (bytes per second) from a device, specified as a list
        of expressions in the format ``PATH:RATE``, where ``RATE`` is either an
        integer number of bytes, or a string ending in ``kb``, ``mb``, or
        ``gb``.

        Examples:

        - ``device_read_bps="/dev/sda:1mb,/dev/sdb:5mb"``
        - ``device_read_bps="['/dev/sda:100mb', '/dev/sdb:5mb']"``

    device_read_iops
        Limit read rate (I/O per second) from a device, specified as a list
        of expressions in the format ``PATH:RATE``, where ``RATE`` is a number
        of I/O operations.

        Examples:

        - ``device_read_iops="/dev/sda:1000,/dev/sdb:500"``
        - ``device_read_iops="['/dev/sda:1000', '/dev/sdb:500']"``

    device_write_bps
        Limit write rate (bytes per second) from a device, specified as a list
        of expressions in the format ``PATH:RATE``, where ``RATE`` is either an
        integer number of bytes, or a string ending in ``kb``, ``mb`` or
        ``gb``.


        Examples:

        - ``device_write_bps="/dev/sda:100mb,/dev/sdb:50mb"``
        - ``device_write_bps="['/dev/sda:100mb', '/dev/sdb:50mb']"``

    device_read_iops
        Limit write rate (I/O per second) from a device, specified as a list
        of expressions in the format ``PATH:RATE``, where ``RATE`` is a number
        of I/O operations.

        Examples:

        - ``device_read_iops="/dev/sda:1000,/dev/sdb:500"``
        - ``device_read_iops="['/dev/sda:1000', '/dev/sdb:500']"``

    dns
        List of DNS nameservers. Can be passed as a comma-separated list or a
        Python list.

        Examples:

        - ``dns=8.8.8.8,8.8.4.4``
        - ``dns="['8.8.8.8', '8.8.4.4']"``

        .. note::

            To skip IP address validation, use ``validate_ip_addrs=False``

    dns_opt
        Additional options to be added to the container’s ``resolv.conf`` file

        Example: ``dns_opt=ndots:9``

    dns_search
        List of DNS search domains. Can be passed as a comma-separated list
        or a Python list.

        Examples:

        - ``dns_search=foo1.domain.tld,foo2.domain.tld``
        - ``dns_search="[foo1.domain.tld, foo2.domain.tld]"``

    domainname
        The domain name to use for the container

        Example: ``domainname=domain.tld``

    entrypoint
        Entrypoint for the container. Either a string (e.g. ``"mycmd --arg1
        --arg2"``) or a Python list (e.g.  ``"['mycmd', '--arg1', '--arg2']"``)

        Examples:

        - ``entrypoint="cat access.log"``
        - ``entrypoint="['cat', 'access.log']"``

    environment (or *env*)
        Either a dictionary of environment variable names and their values, or
        a Python list of strings in the format ``VARNAME=value``.

        Examples:

        - ``environment='VAR1=value,VAR2=value'``
        - ``environment="['VAR1=value', 'VAR2=value']"``
        - ``environment="{'VAR1': 'value', 'VAR2': 'value'}"``

    extra_hosts
        Additional hosts to add to the container's /etc/hosts file. Can be
        passed as a comma-separated list or a Python list. Requires Docker
        1.3.0 or newer.

        Examples:

        - ``extra_hosts=web1:10.9.8.7,web2:10.9.8.8``
        - ``extra_hosts="['web1:10.9.8.7', 'web2:10.9.8.8']"``
        - ``extra_hosts="{'web1': '10.9.8.7', 'web2': '10.9.8.8'}"``

        .. note::

            To skip IP address validation, use ``validate_ip_addrs=False``

    group_add
        List of additional group names and/or IDs that the container process
        will run as

        Examples:

        - ``group_add=web,network``
        - ``group_add="['web', 'network']"``

    hostname
        Hostname of the container. If not provided, and if a ``name`` has been
        provided, the ``hostname`` will default to the ``name`` that was
        passed.

        Example: ``hostname=web1``

        .. warning::

            If the container is started with ``network_mode=host``, the
            hostname will be overridden by the hostname of the Minion.

    interactive (or *stdin_open*): False
        Leave stdin open, even if not attached

        Examples:

        - ``interactive=True``
        - ``stdin_open=True``

    ipc_mode (or *ipc*)
        Set the IPC mode for the container. The default behavior is to create a
        private IPC namespace for the container, but this option can be
        used to change that behavior:

        - ``container:<container_name_or_id>`` reuses another container shared
          memory, semaphores and message queues
        - ``host``: use the host's shared memory, semaphores and message queues

        Examples:

        - ``ipc_mode=container:foo``
        - ``ipc=host``

        .. warning::
            Using ``host`` gives the container full access to local shared
            memory and is therefore considered insecure.

    isolation
        Specifies the type of isolation technology used by containers

        Example: ``isolation=hyperv``

        .. note::
            The default value on Windows server is ``process``, while the
            default value on Windows client is ``hyperv``. On Linux, only
            ``default`` is supported.

    labels (or *label*)
        Add metadata to the container. Labels can be set both with and without
        values:

        Examples:

        - ``labels=foo,bar=baz``
        - ``labels="['foo', 'bar=baz']"``

        .. versionchanged:: 2018.3.0
            Labels both with and without values can now be mixed. Earlier
            releases only permitted one method or the other.

    links
        Link this container to another. Links should be specified in the format
        ``<container_name_or_id>:<link_alias>``. Multiple links can be passed,
        ether as a comma separated list or a Python list.

        Examples:

        - ``links=web1:link1,web2:link2``,
        - ``links="['web1:link1', 'web2:link2']"``
        - ``links="{'web1': 'link1', 'web2': 'link2'}"``

    log_driver
        Set container's logging driver. Requires Docker 1.6 or newer.

        Example:

        - ``log_driver=syslog``

        .. note::
            The logging driver feature was improved in Docker 1.13 introducing
            option name changes. Please see Docker's `Configure logging
            drivers`_ documentation for more information.

        .. _`Configure logging drivers`: https://docs.docker.com/engine/admin/logging/overview/

    log_opt
        Config options for the ``log_driver`` config option. Requires Docker
        1.6 or newer.

        Example:

        - ``log_opt="syslog-address=tcp://192.168.0.42,syslog-facility=daemon"``
        - ``log_opt="['syslog-address=tcp://192.168.0.42', 'syslog-facility=daemon']"``
        - ``log_opt="{'syslog-address': 'tcp://192.168.0.42', 'syslog-facility': 'daemon'}"``

    lxc_conf
        Additional LXC configuration parameters to set before starting the
        container.

        Examples:

        - ``lxc_conf="lxc.utsname=docker,lxc.arch=x86_64"``
        - ``lxc_conf="['lxc.utsname=docker', 'lxc.arch=x86_64']"``
        - ``lxc_conf="{'lxc.utsname': 'docker', 'lxc.arch': 'x86_64'}"``

        .. note::

            These LXC configuration parameters will only have the desired
            effect if the container is using the LXC execution driver, which
            has been deprecated for some time.

    mac_address
        MAC address to use for the container. If not specified, a random MAC
        address will be used.

        Example: ``mac_address=01:23:45:67:89:0a``

    mem_limit (or *memory*) : 0
        Memory limit. Can be specified in bytes or using single-letter units
        (i.e. ``512M``, ``2G``, etc.). A value of ``0`` (the default) means no
        memory limit.

        Examples:

        - ``mem_limit=512M``
        - ``memory=1073741824``

    mem_swappiness
        Tune a container's memory swappiness behavior. Accepts an integer
        between 0 and 100.

        Example: ``mem_swappiness=60``

    memswap_limit (or *memory_swap*) : -1
        Total memory limit (memory plus swap). Set to ``-1`` to disable swap. A
        value of ``0`` means no swap limit.

        Examples:

        - ``memswap_limit=1G``
        - ``memory_swap=2147483648``

    network_disabled : False
        If ``True``, networking will be disabled within the container

        Example: ``network_disabled=True``

    network_mode : bridge
        One of the following:

        - ``bridge`` - Creates a new network stack for the container on the
          docker bridge
        - ``none`` - No networking (equivalent of the Docker CLI argument
          ``--net=none``). Not to be confused with Python's ``None``.
        - ``container:<name_or_id>`` - Reuses another container's network stack
        - ``host`` - Use the host's network stack inside the container

          .. warning::
              Using ``host`` mode gives the container full access to the hosts
              system's services (such as D-Bus), and is therefore considered
              insecure.

        Examples:

        - ``network_mode=null``
        - ``network_mode=container:web1``

    oom_kill_disable
        Whether to disable OOM killer

        Example: ``oom_kill_disable=False``

    oom_score_adj
        An integer value containing the score given to the container in order
        to tune OOM killer preferences

        Example: ``oom_score_adj=500``

    pid_mode
        Set to ``host`` to use the host container's PID namespace within the
        container. Requires Docker 1.5.0 or newer.

        Example: ``pid_mode=host``

    pids_limit
        Set the container's PID limit. Set to ``-1`` for unlimited.

        Example: ``pids_limit=2000``

    port_bindings (or *publish*)
        Bind exposed ports which were exposed using the ``ports`` argument to
        :py:func:`docker.create <salt.modules.dockermod.create>`. These
        should be passed in the same way as the ``--publish`` argument to the
        ``docker run`` CLI command:

        - ``ip:hostPort:containerPort`` - Bind a specific IP and port on the
          host to a specific port within the container.
        - ``ip::containerPort`` - Bind a specific IP and an ephemeral port to a
          specific port within the container.
        - ``hostPort:containerPort`` - Bind a specific port on all of the
          host's interfaces to a specific port within the container.
        - ``containerPort`` - Bind an ephemeral port on all of the host's
          interfaces to a specific port within the container.

        Multiple bindings can be separated by commas, or passed as a Python
        list. The below two examples are equivalent:

        - ``port_bindings="5000:5000,2123:2123/udp,8080"``
        - ``port_bindings="['5000:5000', '2123:2123/udp', 8080]"``

        Port bindings can also include ranges:

        - ``port_bindings="14505-14506:4505-4506"``

        .. note::
            When specifying a protocol, it must be passed in the
            ``containerPort`` value, as seen in the examples above.

    ports
        A list of ports to expose on the container. Can be passed as
        comma-separated list or a Python list. If the protocol is omitted, the
        port will be assumed to be a TCP port.

        Examples:

        - ``ports=1111,2222/udp``
        - ``ports="[1111, '2222/udp']"``

    privileged : False
        If ``True``, runs the exec process with extended privileges

        Example: ``privileged=True``

    publish_all_ports (or *publish_all*): False
        Publish all ports to the host

        Example: ``publish_all_ports=True``

    read_only : False
        If ``True``, mount the container’s root filesystem as read only

        Example: ``read_only=True``

    restart_policy (or *restart*)
        Set a restart policy for the container. Must be passed as a string in
        the format ``policy[:retry_count]`` where ``policy`` is one of
        ``always``, ``unless-stopped``, or ``on-failure``, and ``retry_count``
        is an optional limit to the number of retries. The retry count is ignored
        when using the ``always`` or ``unless-stopped`` restart policy.

        Examples:

        - ``restart_policy=on-failure:5``
        - ``restart_policy=always``

    security_opt
        Security configuration for MLS systems such as SELinux and AppArmor.
        Can be passed as a comma-separated list or a Python list.

        Examples:

        - ``security_opt=apparmor:unconfined,param2:value2``
        - ``security_opt='["apparmor:unconfined", "param2:value2"]'``

        .. important::
            Some security options can contain commas. In these cases, this
            argument *must* be passed as a Python list, as splitting by comma
            will result in an invalid configuration.

        .. note::
            See the documentation for security_opt at
            https://docs.docker.com/engine/reference/run/#security-configuration

    shm_size
        Size of /dev/shm

        Example: ``shm_size=128M``

    stop_signal
        The signal used to stop the container. The default is ``SIGTERM``.

        Example: ``stop_signal=SIGRTMIN+3``

    stop_timeout
        Timeout to stop the container, in seconds

        Example: ``stop_timeout=5``

    storage_opt
        Storage driver options for the container

        Examples:

        - ``storage_opt='dm.basesize=40G'``
        - ``storage_opt="['dm.basesize=40G']"``
        - ``storage_opt="{'dm.basesize': '40G'}"``

    sysctls (or *sysctl*)
        Set sysctl options for the container

        Examples:

        - ``sysctl='fs.nr_open=1048576,kernel.pid_max=32768'``
        - ``sysctls="['fs.nr_open=1048576', 'kernel.pid_max=32768']"``
        - ``sysctls="{'fs.nr_open': '1048576', 'kernel.pid_max': '32768'}"``

    tmpfs
        A map of container directories which should be replaced by tmpfs
        mounts, and their corresponding mount options. Can be passed as Python
        list of PATH:VALUE mappings, or a Python dictionary. However, since
        commas usually appear in the values, this option *cannot* be passed as
        a comma-separated list.

        Examples:

        - ``tmpfs="['/run:rw,noexec,nosuid,size=65536k', '/var/lib/mysql:rw,noexec,nosuid,size=600m']"``
        - ``tmpfs="{'/run': 'rw,noexec,nosuid,size=65536k', '/var/lib/mysql': 'rw,noexec,nosuid,size=600m'}"``

    tty : False
        Attach TTYs

        Example: ``tty=True``

    ulimits (or *ulimit*)
        List of ulimits. These limits should be passed in the format
        ``<ulimit_name>:<soft_limit>:<hard_limit>``, with the hard limit being
        optional. Can be passed as a comma-separated list or a Python list.

        Examples:

        - ``ulimits="nofile=1024:1024,nproc=60"``
        - ``ulimits="['nofile=1024:1024', 'nproc=60']"``

    user
        User under which to run exec process

        Example: ``user=foo``

    userns_mode (or *user_ns_mode*)
        Sets the user namsepace mode, when the user namespace remapping option
        is enabled.

        Example: ``userns_mode=host``

    volumes (or *volume*)
        List of directories to expose as volumes. Can be passed as a
        comma-separated list or a Python list.

        Examples:

        - ``volumes=/mnt/vol1,/mnt/vol2``
        - ``volume="['/mnt/vol1', '/mnt/vol2']"``

    volumes_from
        Container names or IDs from which the container will get volumes. Can
        be passed as a comma-separated list or a Python list.

        Example: ``volumes_from=foo``, ``volumes_from=foo,bar``,
        ``volumes_from="[foo, bar]"``

    volume_driver
        Sets the container's volume driver

        Example: ``volume_driver=foobar``

    working_dir (or *workdir*)
        Working directory inside the container

        Examples:

        - ``working_dir=/var/log/nginx``
        - ``workdir=/var/www/myapp``

    **RETURN DATA**

    A dictionary containing the following keys:

    - ``Id`` - ID of the newly-created container
    - ``Name`` - Name of the newly-created container


    CLI Example:

    .. code-block:: bash

        # Create a data-only container
        salt myminion docker.create myuser/mycontainer volumes="/mnt/vol1,/mnt/vol2"
        # Create a CentOS 7 container that will stay running once started
        salt myminion docker.create centos:7 name=mycent7 interactive=True tty=True command=bash
    """
    if kwargs.pop("inspect", True) and not resolve_image_id(image):
        pull(image, client_timeout=client_timeout)

    kwargs, unused_kwargs = _get_create_kwargs(
        skip_translate=skip_translate,
        ignore_collisions=ignore_collisions,
        validate_ip_addrs=validate_ip_addrs,
        **kwargs
    )

    if unused_kwargs:
        log.warning(
            "The following arguments were ignored because they are not "
            "recognized by docker-py: %s",
            sorted(unused_kwargs),
        )

    log.debug(
        "docker.create: creating container %susing the following " "arguments: %s",
        "with name '{0}' ".format(name) if name is not None else "",
        kwargs,
    )
    time_started = time.time()
    response = _client_wrapper("create_container", image, name=name, **kwargs)
    response["Time_Elapsed"] = time.time() - time_started
    _clear_context()

    if name is None:
        name = inspect_container(response["Id"])["Name"].lstrip("/")
    response["Name"] = name

    if start:
        try:
            start_(name)
        except CommandExecutionError as exc:
            raise CommandExecutionError(
                "Failed to start container after creation",
                info={"response": response, "error": exc.__str__()},
            )
        else:
            response["Started"] = True

    return response