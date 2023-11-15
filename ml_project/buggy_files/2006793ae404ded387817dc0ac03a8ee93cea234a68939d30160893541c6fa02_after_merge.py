    def get_tree_from_tag(self, ref):
        '''
        Return a pygit2.Tree object matching a tag ref fetched into refs/tags/
        '''
        try:
            return self.peel(self.repo.lookup_reference(
                'refs/tags/{0}'.format(ref))).tree
        except KeyError:
            return None