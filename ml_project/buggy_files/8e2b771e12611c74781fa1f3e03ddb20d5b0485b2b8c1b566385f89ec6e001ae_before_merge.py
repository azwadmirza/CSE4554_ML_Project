    def pub(self,
            tgt,
            fun,
            arg=(),
            expr_form='glob',
            ret='',
            jid='',
            timeout=5,
            **kwargs):
        '''
        Take the required arguments and publish the given command.
        Arguments:
            tgt:
                The tgt is a regex or a glob used to match up the ids on
                the minions. Salt works by always publishing every command
                to all of the minions and then the minions determine if
                the command is for them based on the tgt value.
            fun:
                The function name to be called on the remote host(s), this
                must be a string in the format "<modulename>.<function name>"
            arg:
                The arg option needs to be a tuple of arguments to pass
                to the calling function, if left blank
        Returns:
            jid:
                A string, as returned by the publisher, which is the job
                id, this will inform the client where to get the job results
            minions:
                A set, the targets that the tgt passed should match.
        '''
        # Make sure the publisher is running by checking the unix socket
        if not os.path.exists(os.path.join(self.opts['sock_dir'],
                                           'publish_pull.ipc')):
            log.error(
                'Unable to connect to the publisher! '
                'You do not have permissions to access '
                '{0}'.format(self.opts['sock_dir'])
            )
            return {'jid': '0', 'minions': []}

        payload_kwargs = self._prep_pub(
                tgt,
                fun,
                arg,
                expr_form,
                ret,
                jid,
                timeout,
                **kwargs)

        master_uri = 'tcp://' + salt.utils.ip_bracket(self.opts['interface']) + \
                     ':' + str(self.opts['ret_port'])
        channel = salt.transport.Channel.factory(self.opts,
                                                 crypt='clear',
                                                 master_uri=master_uri)

        try:
            payload = channel.send(payload_kwargs, timeout=timeout)
        except SaltReqTimeoutError:
            log.error(
                'Salt request timed out. If this error persists, '
                'worker_threads may need to be increased.'
            )
            return {}

        if not payload:
            # The master key could have changed out from under us! Regen
            # and try again if the key has changed
            key = self.__read_master_key()
            if key == self.key:
                return payload
            self.key = key
            payload_kwargs['key'] = self.key
            payload = channel.send(payload_kwargs)
            if not payload:
                return payload

        # We have the payload, let's get rid of the channel fast(GC'ed faster)
        del channel

        return {'jid': payload['load']['jid'],
                'minions': payload['load']['minions']}