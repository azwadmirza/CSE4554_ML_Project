    def get_src_requirement(self, dist, location, find_tags):
        repo = self.get_url(location)
        if not repo.lower().startswith('git:'):
            repo = 'git+' + repo
        egg_project_name = dist.egg_name().split('-', 1)[0]
        if not repo:
            return None
        current_rev = self.get_revision(location)
        refs = self.get_refs(location)
        # refs maps names to commit hashes; we need the inverse
        # if multiple names map to a single commit, we pick the first one
        # alphabetically
        names_by_commit = {}
        for ref, commit in sorted(refs.items()):
            if commit not in names_by_commit:
                names_by_commit[commit] = ref

        if current_rev in names_by_commit:
            # It's a tag
            full_egg_name = (
                '%s-%s' % (egg_project_name, names_by_commit[current_rev])
            )
        else:
            full_egg_name = '%s-dev' % egg_project_name

        return '%s@%s#egg=%s' % (repo, current_rev, full_egg_name)