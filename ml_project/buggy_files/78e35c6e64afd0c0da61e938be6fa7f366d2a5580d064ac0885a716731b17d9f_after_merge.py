    def fromItem(cls, item):
        """
        :type item: dict
        :rtype: AzureJob
        """
        chunkedJob = item.items()
        chunkedJob.sort()
        if len(chunkedJob) == 1:
            # First element of list = tuple, second element of tuple = serialized job
            wholeJobString = chunkedJob[0][1].value
        else:
            wholeJobString = ''.join(item[1].value for item in chunkedJob)
        return cPickle.loads(bz2.decompress(wholeJobString))