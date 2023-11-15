    def _handle_decoded_payload(self, data):
        '''
        Override this method if you wish to handle the decoded data
        differently.
        '''
        if 'user' in data:
            log.info(
                'User {0[user]} Executing command {0[fun]} with jid '
                '{0[jid]}'.format(data)
            )
        else:
            log.info(
                'Executing command {0[fun]} with jid {0[jid]}'.format(data)
            )
        log.debug('Command details {0}'.format(data))

        if isinstance(data['fun'], six.string_types):
            if data['fun'] == 'sys.reload_modules':
                self.functions, self.returners, self.function_errors, self.executors = self._load_modules()
                self.schedule.functions = self.functions
                self.schedule.returners = self.returners
        # We stash an instance references to allow for the socket
        # communication in Windows. You can't pickle functions, and thus
        # python needs to be able to reconstruct the reference on the other
        # side.
        instance = self
        if self.opts['multiprocessing']:
            if sys.platform.startswith('win'):
                # let python reconstruct the minion on the other side if we're
                # running on windows
                instance = None
            process = multiprocessing.Process(
                target=self._target, args=(instance, self.opts, data)
            )
        else:
            process = threading.Thread(
                target=self._target,
                args=(instance, self.opts, data),
                name=data['jid']
            )
        process.start()
        # TODO: remove the windows specific check?
        if not sys.platform.startswith('win') and self.opts['multiprocessing']:
            # we only want to join() immediately if we are daemonizing a process
            process.join()
        else:
            self.win_proc.append(process)