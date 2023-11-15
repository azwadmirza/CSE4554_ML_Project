    def getDirStream(self, dir):

        stream = bytearray()
        stream.extend(slskmessages.SlskMessage().packObject(NetworkIntType(len(dir))))

        for file_and_meta in dir:
            stream.extend(self.getByteStream(file_and_meta))

        return stream