    def _processBranchChanges(self, new_rev, branch):
        prev_rev = yield self._getCurrentRev(branch)
        if new_rev == prev_rev:
            # Nothing new.
            return
        if prev_rev is None:
            # First time monitoring; start at the top.
            yield self._setCurrentRev(new_rev, branch)
            return

        # two passes for hg log makes parsing simpler (comments is multi-lines)
        revset = '{}::{}'.format(prev_rev, new_rev)
        revListArgs = ['log', '-r', revset, r'--template={rev}:{node}\n']
        results = yield utils.getProcessOutput(self.hgbin, revListArgs,
                                               path=self._absWorkdir(), env=os.environ, errortoo=False)
        results = results.decode(self.encoding)

        revNodeList = [rn.split(':', 1) for rn in results.strip().split()]
        # revsets are inclusive. Strip the already-known "current" changeset.
        if revNodeList:
            del revNodeList[0]
        # empty revNodeList probably means the branch has changed head (strip of force push?)
        # @TODO in that case, we should produce a change for that new rev
        log.msg('hgpoller: processing %d changes in branch %r: %r in %r'
                % (len(revNodeList), branch, revNodeList, self._absWorkdir()))
        for rev, node in revNodeList:
            timestamp, author, files, comments = yield self._getRevDetails(
                node)
            yield self.master.data.updates.addChange(
                author=author,
                committer=None,
                revision=str(node),
                revlink=self.revlink_callable(branch, str(node)),
                files=files,
                comments=comments,
                when_timestamp=int(timestamp) if timestamp else None,
                branch=bytes2unicode(branch),
                category=bytes2unicode(self.category),
                project=bytes2unicode(self.project),
                repository=bytes2unicode(self.repourl),
                src='hg')
            # writing after addChange so that a rev is never missed,
            # but at once to avoid impact from later errors
            yield self._setCurrentRev(new_rev, branch)