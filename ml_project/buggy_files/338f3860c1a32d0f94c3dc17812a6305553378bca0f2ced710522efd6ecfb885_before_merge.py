    def writeAliases(self):
        self.config_lock.acquire()
        f = open(self.filename + ".alias", "wb")
        pickle.dump(self.aliases, f, 1)
        f.close()
        self.config_lock.release()