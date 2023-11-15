    def prepare(cls, profile):
        """
        Prepare for running Borg. This function in the base class should be called from all
        subclasses and calls that define their own `cmd`.

        The `prepare()` step does these things:
        - validate if all conditions to run command are met
        - build borg command

        `prepare()` is run 2x. First at the global level and then for each subcommand.

        :return: dict(ok: book, message: str)
        """
        ret = {'ok': False}

        # Do checks to see if running Borg is possible.
        if cls.is_running():
            ret['message'] = trans_late('messages', 'Backup is already in progress.')
            return ret

        if cls.prepare_bin() is None:
            ret['message'] = trans_late('messages', 'Borg binary was not found.')
            return ret

        if profile.repo is None:
            ret['message'] = trans_late('messages', 'Add a backup repository first.')
            return ret

        if not borg_compat.check('JSON_LOG'):
            ret['message'] = trans_late('messages', 'Your Borg version is too old. >=1.1.0 is required.')
            return ret

        # Try to get password from chosen keyring backend.
        keyring = get_keyring()
        logger.debug("Using %s keyring to store passwords.", keyring.__class__.__name__)
        ret['password'] = keyring.get_password('vorta-repo', profile.repo.url)

        # Try to fall back to DB Keyring, if we use the system keychain.
        if ret['password'] is None and keyring.is_primary:
            logger.debug('Password not found in primary keyring. Falling back to VortaDBKeyring.')
            ret['password'] = VortaDBKeyring().get_password('vorta-repo', profile.repo.url)

            # Give warning and continue if password is found there.
            if ret['password'] is not None:
                logger.warning('Found password in database, but secure storage was available. '
                               'Consider re-adding the repo to use it.')

        ret['ssh_key'] = profile.ssh_key
        ret['repo_id'] = profile.repo.id
        ret['repo_url'] = profile.repo.url
        ret['extra_borg_arguments'] = profile.repo.extra_borg_arguments
        ret['profile_name'] = profile.name

        ret['ok'] = True

        return ret