    def get_tree_from_branch(self, ref):
        '''
        Return a pygit2.Tree object matching a head ref fetched into
        refs/remotes/origin/
        '''
        try:
            return self.repo.lookup_reference(
                'refs/remotes/origin/{0}'.format(ref)).get_object().tree
        except KeyError:
            return None