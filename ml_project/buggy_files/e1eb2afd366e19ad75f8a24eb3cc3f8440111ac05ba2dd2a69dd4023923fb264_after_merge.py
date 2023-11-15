    def run_job(
            self,
            tgt,
            fun,
            arg=(),
            tgt_type='glob',
            ret='',
            timeout=None,
            jid='',
            kwarg=None,
            listen=False,
            **kwargs):
        '''
        Asynchronously send a command to connected minions

        Prep the job directory and publish a command to any targeted minions.

        :return: A dictionary of (validated) ``pub_data`` or an empty
            dictionary on failure. The ``pub_data`` contains the job ID and a
            list of all minions that are expected to return data.

        .. code-block:: python

            >>> local.run_job('*', 'test.sleep', [300])
            {'jid': '20131219215650131543', 'minions': ['jerry']}
        '''
        arg = salt.utils.args.condition_input(arg, kwarg)

        try:
            pub_data = self.pub(
                tgt,
                fun,
                arg,
                tgt_type,
                ret,
                jid=jid,
                timeout=self._get_timeout(timeout),
                listen=listen,
                **kwargs)
        except SaltClientError:
            # Re-raise error with specific message
            raise SaltClientError(
                'The salt master could not be contacted. Is master running?'
            )
        except Exception as general_exception:
            # Convert to generic client error and pass along message
            raise SaltClientError(general_exception)

        return self._check_pub_data(pub_data, listen=listen)