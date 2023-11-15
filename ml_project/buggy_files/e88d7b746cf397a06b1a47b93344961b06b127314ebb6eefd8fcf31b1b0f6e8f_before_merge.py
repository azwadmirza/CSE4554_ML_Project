    def toItem(self, chunkSize=65535):
        """
        :rtype: dict
        """
        item = {}
        serializedAndEncodedJob = base64.b64encode(bz2.compress(cPickle.dumps(self)))
        jobChunks = [serializedAndEncodedJob[i:i + chunkSize]
                     for i in range(0, len(serializedAndEncodedJob), chunkSize)]
        for attributeOrder, chunk in enumerate(jobChunks):
            item['_' + str(attributeOrder).zfill(3)] = chunk
        return item