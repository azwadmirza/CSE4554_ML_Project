    def makeNetworkMessage(self, nozlib=0, rebuild=False):
        # Elaborate hack, to save CPU
        # Store packed message contents in self.built, and use
        # instead of repacking it, unless rebuild is True
        if not rebuild and self.built is not None:
            return self.built
        msg = b""
        msg = msg + self.packObject(len(self.list))
        for (key, value) in self.list.items():
            msg = msg + self.packObject(key.replace(os.sep, "\\")) + value
        if not nozlib:
            self.built = zlib.compress(msg)
        else:
            self.built = msg
        return self.built