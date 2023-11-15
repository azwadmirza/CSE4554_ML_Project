    def get_tags_for_hostsystem(self, hostsystem_mid=None):
        """
        Return list of tag object associated with host system
        Args:
            hostsystem_mid: Dynamic object for host system

        Returns: List of tag object associated with the given host system

        """
        return self.get_tags_for_dynamic_obj(mid=hostsystem_mid)