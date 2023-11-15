    def _rabbit_version(self):
        status = self._exec(['status'], True, False, False)

        version_match = re.search('{rabbit,".*","(?P<version>.*)"}', status)
        if version_match:
            return Version(version_match.group('version'))

        return None