    def computeHomeLeoDir(self):
        # lm = self
        homeLeoDir = g.os_path_finalize_join(g.app.homeDir, '.leo')
        if g.os_path_exists(homeLeoDir):
            return homeLeoDir
        ok = g.makeAllNonExistentDirectories(homeLeoDir, force=True)
        return homeLeoDir if ok else '' # #1450