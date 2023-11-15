    def get_tree_from_branch(self, ref):
        '''
        Return a pygit2.Tree object matching a head ref fetched into
        refs/remotes/origin/
        '''
        try:
            return self.peel(self.repo.lookup_reference(
                'refs/remotes/origin/{0}'.format(ref))).tree
        except KeyError:
            return None