    def _check_version(self, distribution, current_version=None):
        try:
            response = requests.get('https://pypi.python.org/pypi/{}/json'.format(distribution))
        except requests.RequestException as exc:
            Logger.get('versioncheck').warning('Version check for %s failed: %s', distribution, exc)
            raise NoReportError.wrap_exc(ServiceUnavailable())
        try:
            data = response.json()
        except ValueError:
            return None
        if current_version is None:
            try:
                current_version = get_distribution(distribution).version
            except DistributionNotFound:
                return None
        current_version = Version(current_version)
        if current_version.is_prerelease:
            # if we are on a prerelease, get the latest one even if it's also a prerelease
            latest_version = Version(data['info']['version'])
        else:
            # if we are stable, get the latest stable version
            versions = [v for v in map(Version, data['releases']) if not v.is_prerelease]
            latest_version = max(versions) if versions else None
        return {'current_version': unicode(current_version),
                'latest_version': unicode(latest_version) if latest_version else None,
                'outdated': (current_version < latest_version) if latest_version else False}