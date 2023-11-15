    def get_global_region(self, yamlcfg):
        """
        Returns a list of regions defined under global region in the yml config file.

        :param yamlcfg: Content of the yml config file
        :return: List of regions

        """
        g_regions = []
        for keys in yamlcfg['global'].keys():
            if 'region' in keys:
                try:
                    iter(yamlcfg['global']['regions'])
                    namespace = 'global'
                    for region in yamlcfg['global']['regions']:
                        # print("found region %s" % region)
                        g_regions.append(region)
                        self._use_global = True
                except TypeError:
                    print("No regions defined in [%s]:" % namespace)
                    print("Please correct region defs[%s]:" % namespace)
        return g_regions