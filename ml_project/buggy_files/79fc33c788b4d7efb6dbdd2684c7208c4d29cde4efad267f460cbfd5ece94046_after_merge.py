    def build_entity(self):
        return otypes.Network(
            id=self._network_id,
            name=self._module.params['name'],
            required=self._cluster_network.get('required'),
            display=self._cluster_network.get('display'),
            usages=list(set([
                otypes.NetworkUsage(usage)
                for usage in ['display', 'gluster', 'migration']
                if self._cluster_network.get(usage, False)
            ] + self._old_usages))
            if (
                self._cluster_network.get('display') is not None or
                self._cluster_network.get('gluster') is not None or
                self._cluster_network.get('migration') is not None
            ) else None,
        )