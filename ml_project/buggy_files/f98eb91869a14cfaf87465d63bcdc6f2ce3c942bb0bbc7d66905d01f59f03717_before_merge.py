    def get_last_remote_commit(self):
        '''
        Returns latest remote commit we know.
        '''
        return self.git_repo.commit('origin/%s' % self.branch)