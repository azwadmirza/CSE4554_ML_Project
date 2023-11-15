    def get_last_remote_commit(self):
        '''
        Returns latest remote commit we know.
        '''
        try:
            return self.git_repo.commit('origin/%s' % self.branch)
        except ODBError:
            # Try to reread git database in case our in memory object is not
            # up to date with it.
            self.reset_git_repo()
            return self.git_repo.commit('origin/%s' % self.branch)