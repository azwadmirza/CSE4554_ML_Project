    def makeNetworkMessage(self):
        filelist = []
        for i in self.list:
            try:
                filelist.append(self.fileindex[str(i)])
            except Exception:
                pass

        queuesize = self.inqueue[0]

        msg = bytearray()
        msg.extend(
            self.packObject(self.user) +
            self.packObject(NetworkIntType(self.token)) +
            self.packObject(NetworkIntType(len(filelist)))
        )
        for i in filelist:
            msg.extend(
                bytes([1]) +
                self.packObject(i[0]. replace(os. sep, "\\")) +
                self.packObject(NetworkLongLongType(i[1]))
            )
            if i[2] is None:
                # No metadata
                msg.extend(self.packObject('') + self.packObject(0))
            else:
                # FileExtension, NumAttributes,
                msg.extend(self.packObject("mp3") + self.packObject(3))
                msg.extend(
                    self.packObject(0) +
                    self.packObject(NetworkIntType(i[2][0])) +
                    self.packObject(1) +
                    self.packObject(NetworkIntType(i[3])) +
                    self.packObject(2) +
                    self.packObject(i[2][1])
                )
        msg.extend(
            bytes([self.freeulslots]) +
            self.packObject(NetworkIntType(self.ulspeed)) +
            self.packObject(NetworkIntType(queuesize))
        )

        return zlib.compress(msg)