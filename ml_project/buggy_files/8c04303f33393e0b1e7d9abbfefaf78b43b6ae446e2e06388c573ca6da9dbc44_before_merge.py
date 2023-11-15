    def getDirStream(self, dir):

        msg = slskmessages.SlskMessage()
        stream = msg.packObject(NetworkIntType(len(dir)))

        for file_and_meta in dir:
            stream += self.getByteStream(file_and_meta)

        return stream