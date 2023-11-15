def innerLoop(jobStore, config, batchSystem, toilState, jobBatcher, serviceManager, statsAndLogging):
    """
    :param toil.jobStores.abstractJobStore.AbstractJobStore jobStore:
    :param toil.common.Config config:
    :param toil.batchSystems.abstractBatchSystem.AbstractBatchSystem batchSystem:
    :param ToilState toilState:
    :param JobBatcher jobBatcher:
    :param ServiceManager serviceManager:
    :param StatsAndLogging statsAndLogging:
    """
    # Putting this in separate function for easier reading

    # Sets up the timing of the jobWrapper rescuing method
    timeSinceJobsLastRescued = time.time()

    logger.info("Starting the main loop")
    while True:
        # Process jobs that are ready to be scheduled/have successors to schedule
        if len(toilState.updatedJobs) > 0:
            logger.debug('Built the jobs list, currently have %i jobs to update and %i jobs issued',
                         len(toilState.updatedJobs), jobBatcher.getNumberOfJobsIssued())

            updatedJobs = toilState.updatedJobs # The updated jobs to consider below
            toilState.updatedJobs = set() # Resetting the list for the next set

            for jobWrapper, resultStatus in updatedJobs:

                logger.debug('Updating status of job: %s with result status: %s',
                             jobWrapper.jobStoreID, resultStatus)

                # This stops a job with services being issued by the serviceManager from
                # being considered further in this loop. This catch is necessary because
                # the job's service's can fail while being issued, causing the job to be
                # added to updated jobs.
                if jobWrapper in serviceManager.jobWrappersWithServicesBeingStarted:
                    logger.debug("Got a job to update which is still owned by the service "
                                 "manager: %s", jobWrapper.jobStoreID)
                    continue

                # If some of the jobs successors failed then either fail the job
                # or restart it if it has retries left and is a checkpoint job
                if jobWrapper.jobStoreID in toilState.hasFailedSuccessors:

                    # If the job has services running, signal for them to be killed
                    # once they are killed then the jobWrapper will be re-added to the
                    # updatedJobs set and then scheduled to be removed
                    if jobWrapper.jobStoreID in toilState.servicesIssued:
                        logger.debug("Telling job: %s to terminate its services due to successor failure",
                                     jobWrapper.jobStoreID)
                        serviceManager.killServices(toilState.servicesIssued[jobWrapper.jobStoreID],
                                                    error=True)

                    # If the job has non-service jobs running wait for them to finish
                    # the job will be re-added to the updated jobs when these jobs are done
                    elif jobWrapper.jobStoreID in toilState.successorCounts:
                        logger.debug("Job: %s with failed successors still has successor jobs running", jobWrapper.jobStoreID)
                        continue

                    # If the job is a checkpoint and has remaining retries then reissue it.
                    elif jobWrapper.checkpoint is not None and jobWrapper.remainingRetryCount > 0:
                        logger.warn('Job: %s is being restarted as a checkpoint after the total '
                                    'failure of jobs in its subtree.', jobWrapper.jobStoreID)
                        jobBatcher.issueJob(jobWrapper.jobStoreID,
                                            memory=jobWrapper.memory,
                                            cores=jobWrapper.cores,
                                            disk=jobWrapper.disk,
                                            preemptable=jobWrapper.preemptable)
                    else: # Mark it totally failed
                        logger.debug("Job %s is being processed as completely failed", jobWrapper.jobStoreID)
                        jobBatcher.processTotallyFailedJob(jobWrapper)

                # If the jobWrapper has a command it must be run before any successors.
                # Similarly, if the job previously failed we rerun it, even if it doesn't have a
                # command to run, to eliminate any parts of the stack now completed.
                elif jobWrapper.command is not None or resultStatus != 0:
                    isServiceJob = jobWrapper.jobStoreID in toilState.serviceJobStoreIDToPredecessorJob

                    # If the job has run out of retries or is a service job whose error flag has
                    # been indicated, fail the job.
                    if (jobWrapper.remainingRetryCount == 0
                        or isServiceJob and not jobStore.fileExists(jobWrapper.errorJobStoreID)):
                        jobBatcher.processTotallyFailedJob(jobWrapper)
                        logger.warn("Job: %s is completely failed", jobWrapper.jobStoreID)
                    else:
                        # Otherwise try the job again
                        jobBatcher.issueJob(jobWrapper.jobStoreID, jobWrapper.memory,
                                            jobWrapper.cores, jobWrapper.disk, jobWrapper.preemptable)

                # If the job has services to run, which have not been started, start them
                elif len(jobWrapper.services) > 0:
                    # Build a map from the service jobs to the job and a map
                    # of the services created for the job
                    assert jobWrapper.jobStoreID not in toilState.servicesIssued
                    toilState.servicesIssued[jobWrapper.jobStoreID] = {}
                    for serviceJobList in jobWrapper.services:
                        for serviceTuple in serviceJobList:
                            serviceID = serviceTuple[0]
                            assert serviceID not in toilState.serviceJobStoreIDToPredecessorJob
                            toilState.serviceJobStoreIDToPredecessorJob[serviceID] = jobWrapper
                            toilState.servicesIssued[jobWrapper.jobStoreID][serviceID] = serviceTuple[4:7]

                    # Use the service manager to start the services
                    serviceManager.scheduleServices(jobWrapper)

                    logger.debug("Giving job: %s to service manager to schedule its jobs", jobWrapper.jobStoreID)

                # There exist successors to run
                elif len(jobWrapper.stack) > 0:
                    assert len(jobWrapper.stack[-1]) > 0
                    logger.debug("Job: %s has %i successors to schedule",
                                 jobWrapper.jobStoreID, len(jobWrapper.stack[-1]))
                    #Record the number of successors that must be completed before
                    #the jobWrapper can be considered again
                    assert jobWrapper.jobStoreID not in toilState.successorCounts
                    toilState.successorCounts[jobWrapper.jobStoreID] = len(jobWrapper.stack[-1])
                    #List of successors to schedule
                    successors = []
                    #For each successor schedule if all predecessors have been completed
                    for successorJobStoreID, memory, cores, disk, preemptable, predecessorID in jobWrapper.stack.pop():
                        #Build map from successor to predecessors.
                        if successorJobStoreID not in toilState.successorJobStoreIDToPredecessorJobs:
                            toilState.successorJobStoreIDToPredecessorJobs[successorJobStoreID] = []
                        toilState.successorJobStoreIDToPredecessorJobs[successorJobStoreID].append(jobWrapper)
                        #Case that the jobWrapper has multiple predecessors
                        if predecessorID is not None:
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
                        successors.append((successorJobStoreID, memory, cores, disk, preemptable))
                    jobBatcher.issueJobs(successors)

                elif jobWrapper.jobStoreID in toilState.servicesIssued:
                    logger.debug("Telling job: %s to terminate its due to the successful completion of its successor jobs",
                                jobWrapper.jobStoreID)
                    serviceManager.killServices(toilState.servicesIssued[jobWrapper.jobStoreID],
                                                    error=False)

                #There are no remaining tasks to schedule within the jobWrapper, but
                #we schedule it anyway to allow it to be deleted.

                #TODO: An alternative would be simple delete it here and add it to the
                #list of jobs to process, or (better) to create an asynchronous
                #process that deletes jobs and then feeds them back into the set
                #of jobs to be processed
                else:
                    # Remove the job
                    if jobWrapper.remainingRetryCount > 0:
                        jobBatcher.issueJob(jobWrapper.jobStoreID,
                                            config.defaultMemory,
                                            config.defaultCores,
                                            config.defaultDisk,
                                            True) #We allow this cleanup to potentially occur on a preemptable instance
                        logger.debug("Job: %s is empty, we are scheduling to clean it up", jobWrapper.jobStoreID)
                    else:
                        jobBatcher.processTotallyFailedJob(jobWrapper)
                        logger.warn("Job: %s is empty but completely failed - something is very wrong", jobWrapper.jobStoreID)

        # The exit criterion
        if len(toilState.updatedJobs) == 0 and jobBatcher.getNumberOfJobsIssued() == 0 and serviceManager.serviceJobsIssuedToServiceManager == 0:
            logger.info("No jobs left to run so exiting.")
            break

        # Start any service jobs available from the service manager
        while True:
            serviceJobTuple = serviceManager.getServiceJobsToStart(0)
            # Stop trying to get jobs when function returns None
            if serviceJobTuple is None:
                break
            serviceJobStoreID, memory, cores, disk = serviceJobTuple
            logger.debug('Launching service job: %s', serviceJobStoreID)
            # This loop issues the jobs to the batch system because the batch system is not
            # thread-safe. FIXME: don't understand this comment
            jobBatcher.issueJob(serviceJobStoreID, memory, cores, disk, False)

        # Get jobs whose services have started
        while True:
            jobWrapper = serviceManager.getJobWrapperWhoseServicesAreRunning(0)
            if jobWrapper is None: # Stop trying to get jobs when function returns None
                break
            logger.debug('Job: %s has established its services.', jobWrapper.jobStoreID)
            jobWrapper.services = []
            toilState.updatedJobs.add((jobWrapper, 0))

        # Gather any new, updated jobWrapper from the batch system
        updatedJob = batchSystem.getUpdatedBatchJob(2)
        if updatedJob is not None:
            jobBatchSystemID, result, wallTime = updatedJob
            if jobBatcher.hasJob(jobBatchSystemID):
                if result == 0:
                    logger.debug('Batch system is reporting that the jobWrapper with '
                                 'batch system ID: %s and jobWrapper store ID: %s ended successfully',
                                 jobBatchSystemID, jobBatcher.getJob(jobBatchSystemID))
                else:
                    logger.warn('Batch system is reporting that the jobWrapper with '
                                'batch system ID: %s and jobWrapper store ID: %s failed with exit value %i',
                                jobBatchSystemID, jobBatcher.getJob(jobBatchSystemID), result)
                jobBatcher.processFinishedJob(jobBatchSystemID, result, wallTime=wallTime)
            else:
                logger.warn("A result seems to already have been processed "
                            "for jobWrapper with batch system ID: %i", jobBatchSystemID)
        else:
            # Process jobs that have gone awry

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

        # Check on the associated processes and exit if a failure is detected
        statsAndLogging.check()
        serviceManager.check()

    logger.info("Finished the main loop")

    # Consistency check the toil state
    assert toilState.updatedJobs == set()
    assert toilState.successorCounts == {}
    assert toilState.successorJobStoreIDToPredecessorJobs == {}
    assert toilState.serviceJobStoreIDToPredecessorJob == {}
    assert toilState.servicesIssued == {}