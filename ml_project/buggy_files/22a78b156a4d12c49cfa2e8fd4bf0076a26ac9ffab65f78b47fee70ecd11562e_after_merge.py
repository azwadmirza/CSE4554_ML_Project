    def get_global_region(self, yamlcfg):
        """
        Returns a list of regions defined under global region in the yml config file.

        :param yamlcfg: Content of the yml config file
        :return: List of regions

        """
        g_regions = []
        for keys in yamlcfg['global'].keys():
            if 'region' in keys:
                namespace = 'global'
                try:
                    iter(yamlcfg['global']['regions'])
                    for region in yamlcfg['global']['regions']:
                        g_regions.append(region)
                        self._use_global = True
                except TypeError as e:
                    print(PrintMsg.ERROR + "No regions defined in [%s]:" % namespace)
                    print(PrintMsg.ERROR + "Please correct region defs[%s]:" % namespace)
        return g_regions