    def writeAliases(self):
        self.config_lock.acquire()
        f = open(self.filename + ".alias", "wb")
        pickle.dump(self.aliases, f, protocol=pickle.HIGHEST_PROTOCOL)
        f.close()
        self.config_lock.release()