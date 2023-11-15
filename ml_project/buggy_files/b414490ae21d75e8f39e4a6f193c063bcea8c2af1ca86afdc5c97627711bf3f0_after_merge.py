    def __init__(self, host,
                 user=None, password=None, port=None,
                 pkey=None,
                 num_retries=DEFAULT_RETRIES,
                 retry_delay=RETRY_DELAY,
                 allow_agent=True, timeout=None,
                 forward_ssh_agent=False,
                 proxy_host=None,
                 proxy_port=None,
                 proxy_pkey=None,
                 proxy_user=None,
                 proxy_password=None,
                 _auth_thread_pool=True, keepalive_seconds=60,
                 identity_auth=True,):
        """:param host: Host name or IP to connect to.
        :type host: str
        :param user: User to connect as. Defaults to logged in user.
        :type user: str
        :param password: Password to use for password authentication.
        :type password: str
        :param port: SSH port to connect to. Defaults to SSH default (22)
        :type port: int
        :param pkey: Private key file path to use for authentication. Path must
          be either absolute path or relative to user home directory
          like ``~/<path>``.
        :type pkey: str
        :param num_retries: (Optional) Number of connection and authentication
          attempts before the client gives up. Defaults to 3.
        :type num_retries: int
        :param retry_delay: Number of seconds to wait between retries. Defaults
          to :py:class:`pssh.constants.RETRY_DELAY`
        :type retry_delay: int
        :param timeout: SSH session timeout setting in seconds. This controls
          timeout setting of authenticated SSH sessions.
        :type timeout: int
        :param allow_agent: (Optional) set to False to disable connecting to
          the system's SSH agent
        :type allow_agent: bool
        :param identity_auth: (Optional) set to False to disable attempting to
          authenticate with default identity files from
          `pssh.clients.base.single.BaseSSHClient.IDENTITIES`
        :type identity_auth: bool
        :param forward_ssh_agent: Unused - agent forwarding not implemented.
        :type forward_ssh_agent: bool
        :param proxy_host: Connect to target host via given proxy host.
        :type proxy_host: str
        :param proxy_port: Port to use for proxy connection. Defaults to self.port
        :type proxy_port: int
        :param keepalive_seconds: Interval of keep alive messages being sent to
          server. Set to ``0`` or ``False`` to disable.

        :raises: :py:class:`pssh.exceptions.PKeyFileError` on errors finding
          provided private key.
        """
        self.forward_ssh_agent = forward_ssh_agent
        self._forward_requested = False
        self.keepalive_seconds = keepalive_seconds
        self._keepalive_greenlet = None
        self._proxy_client = None
        self.host = host
        self.port = port if port is not None else 22
        if proxy_host is not None:
            _port = port if proxy_port is None else proxy_port
            _pkey = pkey if proxy_pkey is None else proxy_pkey
            _user = user if proxy_user is None else proxy_user
            _password = password if proxy_password is None else proxy_password
            proxy_port = self._connect_proxy(
                proxy_host, _port, _pkey, user=_user, password=_password,
                num_retries=num_retries, retry_delay=retry_delay,
                allow_agent=allow_agent,
                timeout=timeout,
                keepalive_seconds=keepalive_seconds,
                identity_auth=identity_auth,
            )
            proxy_host = '127.0.0.1'
        super(SSHClient, self).__init__(
            host, user=user, password=password, port=port, pkey=pkey,
            num_retries=num_retries, retry_delay=retry_delay,
            allow_agent=allow_agent, _auth_thread_pool=_auth_thread_pool,
            timeout=timeout,
            proxy_host=proxy_host, proxy_port=proxy_port,
            identity_auth=identity_auth)