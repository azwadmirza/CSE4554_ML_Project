    def prepare(cls, params):
        """
        Used to validate existing repository when added.
        """

        # Build fake profile because we don't have it in the DB yet.
        profile = FakeProfile(
            FakeRepo(params['repo_url'], 999, params['extra_borg_arguments']),
            'New Repo',
            params['ssh_key']
        )

        ret = super().prepare(profile)
        if not ret['ok']:
            return ret
        else:
            ret['ok'] = False  # Set back to false, so we can do our own checks here.

        cmd = ["borg", "info", "--info", "--json", "--log-json"]
        cmd.append(profile.repo.url)

        ret['additional_env'] = {
            'BORG_UNKNOWN_UNENCRYPTED_REPO_ACCESS_IS_OK': "yes",
            'BORG_RSH': 'ssh -oStrictHostKeyChecking=no'
        }

        if params['password'] == '':
            ret['password'] = '999999'  # Dummy password if the user didn't supply one. To avoid prompt.
        else:
            ret['password'] = params['password']
        ret['ok'] = True
        ret['cmd'] = cmd

        return ret