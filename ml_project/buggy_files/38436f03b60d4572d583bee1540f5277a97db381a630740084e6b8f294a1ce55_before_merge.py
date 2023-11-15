    def callback(fileHandle):
        stats = json.load(fileHandle, object_hook=Expando)
        workers = stats.workers
        try:
            logs = workers.log
        except AttributeError:
            # To be expected if there were no calls to logToMaster()
            pass
        else:
            for message in logs:
                logger.log(int(message.level),
                           "Got message from job at time: %s : %s",
                           time.strftime("%m-%d-%Y %H:%M:%S"), message.text)

        for log in stats.logs:
            logger.info("%s:     %s", log.jobStoreID, log.text)