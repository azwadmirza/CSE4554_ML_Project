    def __init__(self):
        threading.Thread.__init__(self, name="objectProcessor")
        random.seed()
        # It may be the case that the last time Bitmessage was running,
        # the user closed it before it finished processing everything in the
        # objectProcessorQueue. Assuming that Bitmessage wasn't closed
        # forcefully, it should have saved the data in the queue into the
        # objectprocessorqueue table. Let's pull it out.
        sql_ready.wait()
        queryreturn = sqlQuery(
            '''SELECT objecttype, data FROM objectprocessorqueue''')
        for row in queryreturn:
            objectType, data = row
            queues.objectProcessorQueue.put((objectType, data))
        sqlExecute('''DELETE FROM objectprocessorqueue''')
        logger.debug(
            'Loaded %s objects from disk into the objectProcessorQueue.',
            len(queryreturn))
        self._ack_obj = bmproto.BMStringParser()
        self.successfullyDecryptMessageTimings = []