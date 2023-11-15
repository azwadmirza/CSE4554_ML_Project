    def toItem(self, chunkSize=maxAzureTablePropertySize):
        """
        :param chunkSize: the size of a chunk for splitting up the serialized job into chunks
        that each fit into a property value of the an Azure table entity
        :rtype: dict
        """
        assert chunkSize <= maxAzureTablePropertySize
        item = {}
        serializedAndEncodedJob = bz2.compress(cPickle.dumps(self))
        jobChunks = [serializedAndEncodedJob[i:i + chunkSize]
                     for i in range(0, len(serializedAndEncodedJob), chunkSize)]
        for attributeOrder, chunk in enumerate(jobChunks):
            item['_' + str(attributeOrder).zfill(3)] = EntityProperty('Edm.Binary', chunk)
        return item