def main():
    parser = getBasicOptionParser()

    parser.add_argument("jobStore", type=str,
                        help="The location of the job store used by the workflow whose jobs should "
                             "be killed." + jobStoreLocatorHelp)
    parser.add_argument("--version", action='version', version=version)
    options = parseBasicOptions(parser)

    jobStore = Toil.resumeJobStore(options.jobStore)

    logger.info("Starting routine to kill running jobs in the toil workflow: %s" % options.jobStore)
    ####This behaviour is now broken
    batchSystem = Toil.createBatchSystem(jobStore.config) #This should automatically kill the existing jobs.. so we're good.
    for jobID in batchSystem.getIssuedBatchJobIDs(): #Just in case we do it again.
        batchSystem.killBatchJobs(jobID)
    logger.info("All jobs SHOULD have been killed")