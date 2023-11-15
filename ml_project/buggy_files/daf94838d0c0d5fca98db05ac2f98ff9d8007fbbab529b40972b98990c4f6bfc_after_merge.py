    def _rabbit_version(self):
        status = self._exec(['status'], True, False, False)

        # 3.7.x erlang style output
        version_match = re.search('{rabbit,".*","(?P<version>.*)"}', status)
        if version_match:
            return Version(version_match.group('version'))

        # 3.8.x style ouput
        version_match = re.search('RabbitMQ version: (?P<version>.*)', status)
        if version_match:
            return Version(version_match.group('version'))

        return None