    def computeHomeLeoDir(self):
        # lm = self
        homeLeoDir = g.os_path_finalize_join(g.app.homeDir, '.leo')
        if not g.os_path_exists(homeLeoDir):
            g.makeAllNonExistentDirectories(homeLeoDir, force=True)
        return homeLeoDir