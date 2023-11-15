    def __repr__(self):
        """Return repr of all info
        """
        return \
            "LinuxDistribution(" \
            "os_release_file={0!r}, " \
            "distro_release_file={1!r}, " \
            "_os_release_info={2!r}, " \
            "_lsb_release_info={3!r}, " \
            "_distro_release_info={4!r})".format(
                self.os_release_file,
                self.distro_release_file,
                self._os_release_info,
                self._lsb_release_info,
                self._distro_release_info)