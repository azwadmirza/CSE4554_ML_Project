def mainLoop(config, batchSystem, jobStore, rootJobWrapper):
    """
    This is the main loop from which jobs are issued and processed.
    
    :raises: toil.leader.FailedJobsException if at the end of function their remain
    failed jobs
    
    :return: The return value of the root job's run function.
    """

    ##########################################
    #Get a snap shot of the current state of the jobs in the jobStore
    ##########################################

    toilState = ToilState(jobStore, rootJobWrapper)

    ##########################################
    #Load the jobBatcher class - used to track jobs submitted to the batch-system
    ##########################################

    #Kill any jobs on the batch system queue from the last time.
    assert len(batchSystem.getIssuedBatchJobIDs()) == 0 #Batch system must start with no active jobs!
    logger.info("Checked batch system has no running jobs and no updated jobs")

    jobBatcher = JobBatcher(config, batchSystem, jobStore, toilState)
    logger.info("Found %s jobs to start and %i jobs with successors to run",
                len(toilState.updatedJobs), len(toilState.successorCounts))

    ##########################################
    #Start the stats/logging aggregation process
    ##########################################

    stopStatsAndLoggingAggregatorProcess = Queue() #When this is s
    worker = Process(target=statsAndLoggingAggregatorProcess,
                     args=(jobStore, stopStatsAndLoggingAggregatorProcess))
    worker.start()

    ##########################################
    #The main loop in which jobs are scheduled/processed
    ##########################################

    #Sets up the timing of the jobWrapper rescuing method
    timeSinceJobsLastRescued = time.time()
    #Number of jobs that can not be completed successful after exhausting retries
    totalFailedJobs = 0
    logger.info("Starting the main loop")
    while True:
        ##########################################
        #Process jobs that are ready to be scheduled/have successors to schedule
        ##########################################

        if len(toilState.updatedJobs) > 0:
            logger.debug("Built the jobs list, currently have %i jobs to update and %i jobs issued",
                         len(toilState.updatedJobs), jobBatcher.getNumberOfJobsIssued())

            for jobWrapper, resultStatus in toilState.updatedJobs:
                #If the jobWrapper has a command it must be run before any successors
                #Similarly, if the job previously failed we rerun it, even if it doesn't have a command to
                #run, to eliminate any parts of the stack now completed.
                if jobWrapper.command != None or resultStatus != 0:
                    if jobWrapper.remainingRetryCount > 0:
                        jobBatcher.issueJob(jobWrapper.jobStoreID, jobWrapper.memory,
                                            jobWrapper.cores, jobWrapper.disk)
                    else:
                        totalFailedJobs += 1
                        logger.warn("Job: %s is completely failed", jobWrapper.jobStoreID)

                #There exist successors to run
                elif len(jobWrapper.stack) > 0:
                    assert len(jobWrapper.stack[-1]) > 0
                    logger.debug("Job: %s has %i successors to schedule",
                                 jobWrapper.jobStoreID, len(jobWrapper.stack[-1]))
                    #Record the number of successors that must be completed before
                    #the jobWrapper can be considered again
                    assert jobWrapper not in toilState.successorCounts
                    toilState.successorCounts[jobWrapper] = len(jobWrapper.stack[-1])
                    #List of successors to schedule
                    successors = []
                    #For each successor schedule if all predecessors have been completed
                    for successorJobStoreID, memory, cores, disk, predecessorID in jobWrapper.stack.pop():
                        #Build map from successor to predecessors.
                        if successorJobStoreID not in toilState.successorJobStoreIDToPredecessorJobs:
                            toilState.successorJobStoreIDToPredecessorJobs[successorJobStoreID] = []
                        toilState.successorJobStoreIDToPredecessorJobs[successorJobStoreID].append(jobWrapper)
                        #Case that the jobWrapper has multiple predecessors
                        if predecessorID != None:
                            #Load the wrapped jobWrapper
                            job2 = jobStore.load(successorJobStoreID)
                            #Remove the predecessor from the list of predecessors
                            job2.predecessorsFinished.add(predecessorID)
                            #Checkpoint
                            jobStore.update(job2)
                            #If the jobs predecessors have all not all completed then
                            #ignore the jobWrapper
                            assert len(job2.predecessorsFinished) >= 1
                            assert len(job2.predecessorsFinished) <= job2.predecessorNumber
                            if len(job2.predecessorsFinished) < job2.predecessorNumber:
                                continue
                        successors.append((successorJobStoreID, memory, cores, disk))
                    jobBatcher.issueJobs(successors)

                #There are no remaining tasks to schedule within the jobWrapper, but
                #we schedule it anyway to allow it to be deleted.

                #TODO: An alternative would be simple delete it here and add it to the
                #list of jobs to process, or (better) to create an asynchronous
                #process that deletes jobs and then feeds them back into the set
                #of jobs to be processed
                else:
                    if jobWrapper.remainingRetryCount > 0:
                        jobBatcher.issueJob(jobWrapper.jobStoreID,
                                            config.defaultMemory,
                                            config.defaultCores,
                                            config.defaultDisk)
                        logger.debug("Job: %s is empty, we are scheduling to clean it up", jobWrapper.jobStoreID)
                    else:
                        totalFailedJobs += 1
                        logger.warn("Job: %s is empty but completely failed - something is very wrong", jobWrapper.jobStoreID)

            toilState.updatedJobs = set() #We've considered them all, so reset

        ##########################################
        #The exit criterion
        ##########################################

        if jobBatcher.getNumberOfJobsIssued() == 0:
            logger.info("Only failed jobs and their dependents (%i total) are remaining, so exiting.", totalFailedJobs)
            break

        ##########################################
        #Gather any new, updated jobWrapper from the batch system
        ##########################################

        #Asks the batch system what jobs have been completed,
        #give
        updatedJob = batchSystem.getUpdatedBatchJob(10)
        if updatedJob != None:
            jobBatchSystemID, result = updatedJob
            if jobBatcher.hasJob(jobBatchSystemID):
                if result == 0:
                    logger.debug("Batch system is reporting that the jobWrapper with "
                                 "batch system ID: %s and jobWrapper store ID: %s ended successfully",
                                 jobBatchSystemID, jobBatcher.getJob(jobBatchSystemID))
                else:
                    logger.warn("Batch system is reporting that the jobWrapper with "
                                "batch system ID: %s and jobWrapper store ID: %s failed with exit value %i",
                                jobBatchSystemID, jobBatcher.getJob(jobBatchSystemID), result)
                jobBatcher.processFinishedJob(jobBatchSystemID, result)
            else:
                logger.warn("A result seems to already have been processed "
                            "for jobWrapper with batch system ID: %i", jobBatchSystemID)
        else:
            ##########################################
            #Process jobs that have gone awry
            ##########################################

            #In the case that there is nothing happening
            #(no updated jobWrapper to gather for 10 seconds)
            #check if their are any jobs that have run too long
            #(see JobBatcher.reissueOverLongJobs) or which
            #have gone missing from the batch system (see JobBatcher.reissueMissingJobs)
            if (time.time() - timeSinceJobsLastRescued >=
                config.rescueJobsFrequency): #We only
                #rescue jobs every N seconds, and when we have
                #apparently exhausted the current jobWrapper supply
                jobBatcher.reissueOverLongJobs()
                logger.info("Reissued any over long jobs")

                hasNoMissingJobs = jobBatcher.reissueMissingJobs()
                if hasNoMissingJobs:
                    timeSinceJobsLastRescued = time.time()
                else:
                    timeSinceJobsLastRescued += 60 #This means we'll try again
                    #in a minute, providing things are quiet
                logger.info("Rescued any (long) missing jobs")

    logger.info("Finished the main loop")

    ##########################################
    #Finish up the stats/logging aggregation process
    ##########################################
    logger.info("Waiting for stats and logging collator process to finish")
    startTime = time.time()
    stopStatsAndLoggingAggregatorProcess.put(True)
    worker.join()
    logger.info("Stats/logging finished collating in %s seconds", time.time() - startTime)
    # in addition to cleaning on exceptions, onError should clean if there are any failed jobs

    #Parse out the return value from the root job
    with jobStore.readSharedFileStream("rootJobReturnValue") as fH:
        jobStoreFileID = fH.read()
    with jobStore.readFileStream(jobStoreFileID) as fH:
        rootJobReturnValue = cPickle.load(fH)
    
    if totalFailedJobs > 0:
        if config.clean == "onError" or config.clean == "always" :
            jobStore.deleteJobStore()
        raise FailedJobsException( config.jobStore, totalFailedJobs )

    if config.clean == "onSuccess" or config.clean == "always":
        jobStore.deleteJobStore()

    return rootJobReturnValue