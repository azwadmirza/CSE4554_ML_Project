    def get_distribution_facts(self):
        # The platform module provides information about the running
        # system/distribution. Use this as a baseline and fix buggy systems
        # afterwards
        self.facts['distribution_release'] = platform.release()
        self.facts['distribution_version'] = platform.version()

        systems_platform_working = ('NetBSD', 'FreeBSD')
        systems_implemented = ('AIX', 'HP-UX', 'Darwin', 'OpenBSD')

        if self.system in systems_platform_working:
            # the distribution is provided by platform module already and needs no fixes
            pass

        elif self.system in systems_implemented:
            self.facts['distribution'] = self.system
            cleanedname = self.system.replace('-','')
            distfunc = getattr(self, 'get_distribution_'+cleanedname)
            distfunc()
        elif self.system == 'Linux':
            # try to find out which linux distribution this is
            dist = platform.dist()
            self.facts['distribution'] = dist[0].capitalize() or 'NA'
            self.facts['distribution_version'] = dist[1] or 'NA'
            self.facts['distribution_major_version'] = dist[1].split('.')[0] or 'NA'
            self.facts['distribution_release'] = dist[2] or 'NA'
            # Try to handle the exceptions now ...
            # self.facts['distribution_debug'] = []
            for ddict in self.OSDIST_LIST:
                name = ddict['name']
                path = ddict['path']

                if not os.path.exists(path):
                    continue
                # if allowempty is set, we only check for file existance but not content
                if 'allowempty' in ddict and ddict['allowempty']:
                    self.facts['distribution'] = name
                    break
                if os.path.getsize(path) == 0:
                    continue

                data = get_file_content(path)
                if name in self.SEARCH_STRING:
                    # look for the distribution string in the data and replace according to RELEASE_NAME_MAP
                    # only the distribution name is set, the version is assumed to be correct from platform.dist()
                    if self.SEARCH_STRING[name] in data:
                        # this sets distribution=RedHat if 'Red Hat' shows up in data
                        self.facts['distribution'] = name
                    else:
                        # this sets distribution to what's in the data, e.g. CentOS, Scientific, ...
                        self.facts['distribution'] = data.split()[0]
                    break
                else:
                    # call a dedicated function for parsing the file content
                    try:
                        distfunc = getattr(self, 'get_distribution_' + name)
                        parsed = distfunc(name, data, path)
                        if parsed is None or parsed:
                            # distfunc return False if parsing failed
                            # break only if parsing was succesful
                            # otherwise continue with other distributions
                            break
                    except AttributeError:
                        # this should never happen, but if it does fail quitely and not with a traceback
                        pass



                    # to debug multiple matching release files, one can use:
                    # self.facts['distribution_debug'].append({path + ' ' + name:
                    #         (parsed,
                    #          self.facts['distribution'],
                    #          self.facts['distribution_version'],
                    #          self.facts['distribution_release'],
                    #          )})

        self.facts['os_family'] = self.facts['distribution']
        distro = self.facts['distribution'].replace(' ', '_')
        if distro in self.OS_FAMILY:
            self.facts['os_family'] = self.OS_FAMILY[distro]