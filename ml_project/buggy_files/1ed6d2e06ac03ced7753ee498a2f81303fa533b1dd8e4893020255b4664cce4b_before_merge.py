    def _fetch(self):
        '''
        Fetch the repo. If the local copy was updated, return True. If the
        local copy was already up-to-date, return False.
        '''
        origin = self.repo.remotes[0]
        refs_pre = self.repo.listall_references()
        fetch_kwargs = {}
        if self.credentials is not None:
            if self.use_callback:
                fetch_kwargs['callbacks'] = \
                    pygit2.RemoteCallbacks(credentials=self.credentials)
            else:
                origin.credentials = self.credentials
        try:
            fetch_results = origin.fetch(**fetch_kwargs)
        except GitError as exc:
            # Using exc.__str__() here to avoid deprecation warning
            # when referencing exc.message
            exc_str = exc.__str__().lower()
            if 'unsupported url protocol' in exc_str \
                    and isinstance(self.credentials, pygit2.Keypair):
                log.error(
                    'Unable to fetch SSH-based {0} remote \'{1}\'. '
                    'You may need to add ssh:// to the repo string or '
                    'libgit2 must be compiled with libssh2 to support '
                    'SSH authentication.'.format(self.role, self.id)
                )
            elif 'authentication required but no callback set' in exc_str:
                log.error(
                    '{0} remote \'{1}\' requires authentication, but no '
                    'authentication configured'.format(self.role, self.id)
                )
            else:
                log.error(
                    'Error occured fetching {0} remote \'{1}\': {2}'.format(
                        self.role, self.id, exc
                    )
                )
            return False
        try:
            # pygit2.Remote.fetch() returns a dict in pygit2 < 0.21.0
            received_objects = fetch_results['received_objects']
        except (AttributeError, TypeError):
            # pygit2.Remote.fetch() returns a class instance in
            # pygit2 >= 0.21.0
            received_objects = fetch_results.received_objects
        if received_objects != 0:
            log.debug(
                '{0} received {1} objects for remote \'{2}\''
                .format(self.role, received_objects, self.id)
            )
        else:
            log.debug(
                '{0} remote \'{1}\' is up-to-date'.format(self.role, self.id)
            )
        refs_post = self.repo.listall_references()
        cleaned = self.clean_stale_refs(local_refs=refs_post)
        return bool(received_objects or refs_pre != refs_post or cleaned)