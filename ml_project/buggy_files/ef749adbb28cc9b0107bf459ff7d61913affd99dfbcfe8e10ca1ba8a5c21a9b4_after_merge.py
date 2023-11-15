    def init_remote(self):
        '''
        Initialize/attach to a remote using pygit2. Return a boolean which
        will let the calling function know whether or not a new repo was
        initialized by this function.
        '''
        # https://github.com/libgit2/pygit2/issues/339
        # https://github.com/libgit2/libgit2/issues/2122
        home = os.path.expanduser('~')
        pygit2.settings.search_path[pygit2.GIT_CONFIG_LEVEL_GLOBAL] = home
        new = False
        if not os.listdir(self.cachedir):
            # Repo cachedir is empty, initialize a new repo there
            self.repo = pygit2.init_repository(self.cachedir)
            new = True
        else:
            # Repo cachedir exists, try to attach
            try:
                self.repo = pygit2.Repository(self.cachedir)
            except KeyError:
                log.error(_INVALID_REPO.format(self.cachedir, self.url, self.role))
                return new

        self.gitdir = salt.utils.path_join(self.repo.workdir, '.git')

        if not self.repo.remotes:
            try:
                self.repo.create_remote('origin', self.url)
            except os.error:
                # This exception occurs when two processes are trying to write
                # to the git config at once, go ahead and pass over it since
                # this is the only write. This should place a lock down.
                pass
            else:
                new = True

            try:
                ssl_verify = self.repo.config.get_bool('http.sslVerify')
            except KeyError:
                ssl_verify = None
            if ssl_verify != self.ssl_verify:
                self.repo.config.set_multivar('http.sslVerify',
                                            '',
                                            str(self.ssl_verify).lower())

            # Ensure that refspecs for the "origin" remote are set up as configured
            if hasattr(self, 'refspecs'):
                self.configure_refspecs()

        return new