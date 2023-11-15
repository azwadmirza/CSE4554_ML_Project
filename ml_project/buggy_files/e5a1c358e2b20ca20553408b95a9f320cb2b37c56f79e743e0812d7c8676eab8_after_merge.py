    def fetch(self):
        '''
        Fetch the repo. If the local copy was updated, return True. If the
        local copy was already up-to-date, return False.
        '''
        origin = self.repo.remotes[0]
        refs_pre = self.repo.listall_references()
        credentials = getattr(self, 'credentials', None)
        if credentials is not None:
            origin.credentials = credentials
        try:
            fetch_results = origin.fetch()
        except GitError as exc:
            # Using exc.__str__() here to avoid deprecation warning
            # when referencing exc.message
            if 'unsupported url protocol' in exc.__str__().lower() \
                    and isinstance(credentials, pygit2.Keypair):
                log.error(
                    'Unable to fetch SSH-based {0} remote \'{1}\'. '
                    'libgit2 must be compiled with libssh2 to support '
                    'SSH authentication.'.format(self.role, self.id)
                )
                return False
            raise
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