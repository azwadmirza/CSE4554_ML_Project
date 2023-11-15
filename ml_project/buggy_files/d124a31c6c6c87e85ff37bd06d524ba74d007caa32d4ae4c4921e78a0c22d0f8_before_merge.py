    def _parse_line(self, line):
        """Parse a line from a host file.

        Args:
            line: The bytes object to parse.

        Returns:
            True if parsing succeeded, False otherwise.
        """
        if line.startswith(b'#'):
            # Ignoring comments early so we don't have to care about
            # encoding errors in them.
            return True

        try:
            line = line.decode('utf-8')
        except UnicodeDecodeError:
            log.misc.error("Failed to decode: {!r}".format(line))
            return False

        # Remove comments
        try:
            hash_idx = line.index('#')
            line = line[:hash_idx]
        except ValueError:
            pass

        line = line.strip()
        # Skip empty lines
        if not line:
            return True

        parts = line.split()
        if len(parts) == 1:
            # "one host per line" format
            host = parts[0]
        elif len(parts) == 2:
            # /etc/hosts format
            host = parts[1]
        else:
            log.misc.error("Failed to parse: {!r}".format(line))
            return False

        if host not in self.WHITELISTED:
            self._blocked_hosts.add(host)

        return True