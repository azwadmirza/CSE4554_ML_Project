    def get_resources(self, rids, cache=True):
        # Launch template versions have a compound primary key
        #
        # Support one of four forms of resource ids:
        #
        #  - array of launch template ids
        #  - array of tuples (launch template id, version id)
        #  - array of dicts (with LaunchTemplateId and VersionNumber)
        #  - array of dicts (with LaunchTemplateId and LatestVersionNumber)
        #
        # If an alias version is given $Latest, $Default, the alias will be
        # preserved as an annotation on the returned object 'c7n:VersionAlias'
        if not rids:
            return []

        t_versions = {}
        if isinstance(rids[0], tuple):
            for tid, tversion in rids:
                t_versions.setdefault(tid, []).append(tversion)
        elif isinstance(rids[0], dict):
            for tinfo in rids:
                t_versions.setdefault(
                    tinfo['LaunchTemplateId'], []).append(
                        tinfo.get('VersionNumber', tinfo.get('LatestVersionNumber')))
        elif isinstance(rids[0], six.string_types):
            for tid in rids:
                t_versions[tid] = []

        client = utils.local_session(self.session_factory).client('ec2')

        results = []
        # We may end up fetching duplicates on $Latest and $Version
        for tid, tversions in t_versions.items():
            ltv = client.describe_launch_template_versions(
                LaunchTemplateId=tid, Versions=tversions).get(
                    'LaunchTemplateVersions')
            if not tversions:
                tversions = [str(t['VersionNumber']) for t in ltv]
            for tversion, t in zip(tversions, ltv):
                if not tversion.isdigit():
                    t['c7n:VersionAlias'] = tversion
                results.append(t)
        return results