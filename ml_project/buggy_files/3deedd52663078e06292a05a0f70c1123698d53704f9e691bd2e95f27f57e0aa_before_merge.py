def statsAndLoggingAggregatorProcess(jobStore, stop):
    """
    The following function is used for collating stats/reporting log messages from the workers.
    Works inside of a separate process, collates as long as the stop flag is not True.
    """
    #  Overall timing
    startTime = time.time()
    startClock = getTotalCpuTime()

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

    while True:
        # This is a indirect way of getting a message to the process to exit
        if not stop.empty():
            jobStore.readStatsAndLogging(callback)
            break
        if jobStore.readStatsAndLogging(callback) == 0:
            time.sleep(0.5)  # Avoid cycling too fast

    # Finish the stats file
    text = json.dumps(dict(total_time=str(time.time() - startTime),
                           total_clock=str(getTotalCpuTime() - startClock)))
    jobStore.writeStatsAndLogging(text)