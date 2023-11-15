    def __init__(self, host,
                 user=None, password=None, port=None,
                 pkey=None, forward_ssh_agent=True,
                 num_retries=DEFAULT_RETRIES, agent=None,
                 allow_agent=True, timeout=10, proxy_host=None,
                 proxy_port=22, proxy_user=None, proxy_password=None,
                 proxy_pkey=None, channel_timeout=None,
                 _openssh_config_file=None,
                 **paramiko_kwargs):
        """
        :param host: Hostname to connect to
        :type host: str
        :param user: (Optional) User to login as. Defaults to logged in user or
          user from ~/.ssh/config if set
        :type user: str
        :param password: (Optional) Password to use for login. Defaults to
          no password
        :type password: str
        :param port: (Optional) Port number to use for SSH connection. Defaults
          to ``None`` which uses SSH default
        :type port: int
        :param pkey: (Optional) Client's private key to be used to connect with
        :type pkey: :py:class:`paramiko.pkey.PKey`
        :param num_retries: (Optional) Number of retries for connection attempts
          before the client gives up. Defaults to 3.
        :type num_retries: int
        :param timeout: (Optional) Number of seconds to timeout connection
          attempts before the client gives up
        :type timeout: int
        :param forward_ssh_agent: (Optional) Turn on SSH agent forwarding -
          equivalent to `ssh -A` from the `ssh` command line utility.
          Defaults to True if not set.
        :type forward_ssh_agent: bool
        :param agent: (Optional) Override SSH agent object with the provided.
          This allows for overriding of the default paramiko behaviour of
          connecting to local SSH agent to lookup keys with our own SSH agent
          object.
        :type agent: :py:class:`paramiko.agent.Agent`
        :param forward_ssh_agent: (Optional) Turn on SSH agent forwarding -
          equivalent to `ssh -A` from the `ssh` command line utility.
          Defaults to True if not set.
        :type forward_ssh_agent: bool
        :param proxy_host: (Optional) SSH host to tunnel connection through
          so that SSH clients connects to self.host via
          client -> proxy_host -> host
        :type proxy_host: str
        :param proxy_port: (Optional) SSH port to use to login to proxy host if
          set. Defaults to 22.
        :type proxy_port: int
        :param channel_timeout: (Optional) Time in seconds before an SSH
          operation times out.
        :type channel_timeout: int
        :param allow_agent: (Optional) set to False to disable connecting to
          the SSH agent
        :type allow_agent: bool
        :param paramiko_kwargs: (Optional) Extra keyword arguments to be
          passed on to :py:func:`paramiko.client.SSHClient.connect`
        :type paramiko_kwargs: dict
        """
        try:
            _host, _user, _port, _pkey = read_openssh_config(
                host, config_file=_openssh_config_file)
        except TypeError:
            _host, _user, _port, _pkey = None, None, 22, None
        user = user if user else _user
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
        self.forward_ssh_agent = forward_ssh_agent
        self.client = client
        self.user = user
        self.password = password
        self.pkey = pkey if pkey else _pkey
        self.port = port if port else _port
        self.host = host
        self._host = _host
        self.allow_agent = allow_agent
        if agent:
            self.client._agent = agent
        self.num_retries = num_retries
        self.timeout = timeout
        self.channel_timeout = channel_timeout
        self.proxy_host, self.proxy_port, self.proxy_user, \
            self.proxy_password, self.proxy_pkey = proxy_host, proxy_port, \
            proxy_user, proxy_password, proxy_pkey
        self.proxy_client = None
        real_host = _host if _host is not None else host
        if self.proxy_host and self.proxy_port:
            logger.debug(
                "Proxy configured for destination host %s - Proxy host: %s:%s",
                real_host, self.proxy_host, self.proxy_port,)
            self._connect_tunnel(real_host, **paramiko_kwargs)
        else:
            self._connect(self.client, real_host, self.port, **paramiko_kwargs)