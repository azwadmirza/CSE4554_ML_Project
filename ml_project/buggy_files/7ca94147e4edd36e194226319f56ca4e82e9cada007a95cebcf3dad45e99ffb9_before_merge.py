    def makeNetworkMessage(self):
        msg = self.packObject(1) + self.packObject(self.dir) + self.packObject(1) + self.packObject(self.dir) + self.packObject(len(self.list))
        for i in self.list:
            msg = msg + bytes([1]) + self.packObject(i[0]) + self.packObject(i[1]) + self.packObject(0)
            if i[2] is None:
                msg = msg + self.packObject('') + self.packObject(0)
            else:
                msg = msg + self.packObject("mp3") + self.packObject(2)
                msg = msg + self.packObject(0) + self.packObject(i[2]) + self.packObject(1) + self.packObject(i[3])
        return zlib.compress(msg)