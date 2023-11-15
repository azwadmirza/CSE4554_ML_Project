    def prepare(cls, params):

        # Build fake profile because we don't have it in the DB yet.
        profile = FakeProfile(
            FakeRepo(params['repo_url'], 999, params['extra_borg_arguments']), 'Init Repo', params['ssh_key']
        )

        ret = super().prepare(profile)
        if not ret['ok']:
            return ret
        else:
            ret['ok'] = False  # Set back to false, so we can do our own checks here.

        cmd = ["borg", "init", "--info", "--log-json"]
        cmd.append(f"--encryption={params['encryption']}")
        cmd.append(params['repo_url'])

        ret['additional_env'] = {
            'BORG_RSH': 'ssh -oStrictHostKeyChecking=no'
        }

        ret['encryption'] = params['encryption']
        ret['password'] = params['password']
        ret['ok'] = True
        ret['cmd'] = cmd

        return ret