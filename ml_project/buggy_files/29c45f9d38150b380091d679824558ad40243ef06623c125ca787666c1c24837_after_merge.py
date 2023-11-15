    def _connect(self, client, host, port, sock=None, retries=1,
                 user=None, password=None, pkey=None,
                 **paramiko_kwargs):
        """Connect to host

        :raises: :py:class:`pssh.exceptions.AuthenticationException`
          on authentication error
        :raises: :py:class:`pssh.exceptions.UnknownHostException`
          on DNS resolution error
        :raises: :py:class:`pssh.exceptions.ConnectionErrorException`
          on error connecting
        :raises: :py:class:`pssh.exceptions.SSHException` on other undefined
          SSH errors
        """
        logger.debug("Connecting to %s..", host)
        try:
            client.connect(host,
                           username=user if user else self.user,
                           password=password if password else self.password,
                           port=port, pkey=pkey if pkey else self.pkey,
                           sock=sock, timeout=self.timeout,
                           allow_agent=self.allow_agent,
                           **paramiko_kwargs)
        except sock_gaierror as ex:
            logger.error("Could not resolve host '%s' - retry %s/%s",
                         host, retries, self.num_retries)
            while retries < self.num_retries:
                sleep(5)
                return self._connect(client, host, port,
                                     sock=sock,
                                     retries=retries+1,
                                     **paramiko_kwargs)
            raise UnknownHostException("Unknown host %s - %s - retry %s/%s",
                                       host, str(ex.args[1]), retries,
                                       self.num_retries)
        except sock_error as ex:
            logger.error("Error connecting to host '%s:%s' - retry %s/%s",
                         host, self.port, retries, self.num_retries)
            while retries < self.num_retries:
                sleep(5)
                return self._connect(client, host, port,
                                     sock=sock,
                                     retries=retries+1,
                                     **paramiko_kwargs)
            error_type = ex.args[1] if len(ex.args) > 1 else ex.args[0]
            raise ConnectionErrorException(
                "Error connecting to host '%s:%s' - %s - retry %s/%s",
                host, self.port, str(error_type), retries,
                self.num_retries,)
        except paramiko.AuthenticationException as ex:
            msg = "Authentication error while connecting to %s:%s."
            raise AuthenticationException(msg, host, port)
        # SSHException is more general so should be below other types
        # of SSH failure
        except paramiko.SSHException as ex:
            msg = "General SSH error - %s" % (ex,)
            logger.error(msg)
            raise SSHException(msg, host, port)