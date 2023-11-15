    def version_filter(version):
      return (version[MAJOR] == 2 and version[MINOR] >= 7 or
              version[MAJOR] == 3 and version[MINOR] >= 4)