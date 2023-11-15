    def checkout(self):
        '''
        Checkout the configured branch/tag
        '''
        tgt_ref = self.get_checkout_target()
        local_ref = 'refs/heads/' + tgt_ref
        remote_ref = 'refs/remotes/origin/' + tgt_ref
        tag_ref = 'refs/tags/' + tgt_ref

        try:
            local_head = self.repo.lookup_reference('HEAD')
        except KeyError:
            log.warning(
                'HEAD not present in %s remote \'%s\'', self.role, self.id
            )
            return None

        try:
            head_sha = self.peel(local_head).hex
        except AttributeError:
            # Shouldn't happen, but just in case a future pygit2 API change
            # breaks things, avoid a traceback and log an error.
            log.error(
                'Unable to get SHA of HEAD for %s remote \'%s\'',
                self.role, self.id
            )
            return None
        except KeyError:
            head_sha = None

        refs = self.repo.listall_references()

        def _perform_checkout(checkout_ref, branch=True):
            '''
            DRY function for checking out either a branch or a tag
            '''
            try:
                with self.gen_lock(lock_type='checkout'):
                    # Checkout the local branch corresponding to the
                    # remote ref.
                    self.repo.checkout(checkout_ref)
                    if branch:
                        self.repo.reset(oid, pygit2.GIT_RESET_HARD)
                return True
            except GitLockError as exc:
                if exc.errno == errno.EEXIST:
                    # Re-raise with a different strerror containing a
                    # more meaningful error message for the calling
                    # function.
                    raise GitLockError(
                        exc.errno,
                        'Checkout lock exists for {0} remote \'{1}\''
                        .format(self.role, self.id)
                    )
                else:
                    log.error(
                        'Error %d encountered obtaining checkout lock '
                        'for %s remote \'%s\'',
                        exc.errno,
                        self.role,
                        self.id
                    )
            return False

        try:
            if remote_ref in refs:
                # Get commit id for the remote ref
                oid = self.peel(self.repo.lookup_reference(remote_ref)).id
                if local_ref not in refs:
                    # No local branch for this remote, so create one and point
                    # it at the commit id of the remote ref
                    self.repo.create_reference(local_ref, oid)

                try:
                    target_sha = \
                        self.peel(self.repo.lookup_reference(remote_ref)).hex
                except KeyError:
                    log.error(
                        'pygit2 was unable to get SHA for %s in %s remote '
                        '\'%s\'', local_ref, self.role, self.id,
                        exc_info=True
                    )
                    return None

                # Only perform a checkout if HEAD and target are not pointing
                # at the same SHA1.
                if head_sha != target_sha:
                    # Check existence of the ref in refs/heads/ which
                    # corresponds to the local HEAD. Checking out local_ref
                    # below when no local ref for HEAD is missing will raise an
                    # exception in pygit2 >= 0.21. If this ref is not present,
                    # create it. The "head_ref != local_ref" check ensures we
                    # don't try to add this ref if it is not necessary, as it
                    # would have been added above already. head_ref would be
                    # the same as local_ref if the branch name was changed but
                    # the cachedir was not (for example if a "name" parameter
                    # was used in a git_pillar remote, or if we are using
                    # winrepo which takes the basename of the repo as the
                    # cachedir).
                    head_ref = local_head.target
                    # If head_ref is not a string, it will point to a
                    # pygit2.Oid object and we are in detached HEAD mode.
                    # Therefore, there is no need to add a local reference. If
                    # head_ref == local_ref, then the local reference for HEAD
                    # in refs/heads/ already exists and again, no need to add.
                    if isinstance(head_ref, six.string_types) \
                            and head_ref not in refs and head_ref != local_ref:
                        branch_name = head_ref.partition('refs/heads/')[-1]
                        if not branch_name:
                            # Shouldn't happen, but log an error if it does
                            log.error(
                                'pygit2 was unable to resolve branch name from '
                                'HEAD ref \'%s\' in %s remote \'%s\'',
                                head_ref, self.role, self.id
                            )
                            return None
                        remote_head = 'refs/remotes/origin/' + branch_name
                        if remote_head not in refs:
                            # No remote ref for HEAD exists. This can happen in
                            # the first-time git_pillar checkout when when the
                            # remote repo does not have a master branch. Since
                            # we need a HEAD reference to keep pygit2 from
                            # throwing an error, and none exists in
                            # refs/remotes/origin, we'll just point HEAD at the
                            # remote_ref.
                            remote_head = remote_ref
                        self.repo.create_reference(
                            head_ref,
                            self.repo.lookup_reference(remote_head).target
                        )

                    if not _perform_checkout(local_ref, branch=True):
                        return None

                # Return the relative root, if present
                return self.check_root()

            elif tag_ref in refs:
                tag_obj = self.repo.revparse_single(tag_ref)
                if not isinstance(tag_obj, pygit2.Commit):
                    log.error(
                        '%s does not correspond to pygit2.Commit object',
                        tag_ref
                    )
                else:
                    try:
                        # If no AttributeError raised, this is an annotated tag
                        tag_sha = tag_obj.target.hex
                    except AttributeError:
                        try:
                            tag_sha = tag_obj.hex
                        except AttributeError:
                            # Shouldn't happen, but could if a future pygit2
                            # API change breaks things.
                            log.error(
                                'Unable to resolve %s from %s remote \'%s\' '
                                'to either an annotated or non-annotated tag',
                                tag_ref, self.role, self.id,
                                exc_info=True
                            )
                            return None
                    log.debug('SHA of tag %s: %s', tgt_ref, tag_sha)

                    if head_sha != tag_sha:
                        if not _perform_checkout(tag_ref, branch=False):
                            return None

                    # Return the relative root, if present
                    return self.check_root()
        except GitLockError:
            raise
        except Exception as exc:
            log.error(
                'Failed to checkout %s from %s remote \'%s\': %s',
                tgt_ref, self.role, self.id, exc,
                exc_info=True
            )
            return None
        log.error(
            'Failed to checkout %s from %s remote \'%s\': remote ref '
            'does not exist', tgt_ref, self.role, self.id
        )
        return None