def main():
    parser = getBasicOptionParser()

    parser.add_argument("jobStore", type=str,
              help=("Store in which to place job management files \
              and the global accessed temporary files"
              "(If this is a file path this needs to be globally accessible "
              "by all machines running jobs).\n"
              "If the store already exists and restart is false an"
              " JobStoreCreationException exception will be thrown."))
    parser.add_argument("--version", action='version', version=version)
    options = parseBasicOptions(parser)

    jobStore = Toil.loadOrCreateJobStore(options.jobStore)
    
    logger.info("Starting routine to kill running jobs in the toil workflow: %s" % options.jobStore)
    ####This behaviour is now broken
    batchSystem = Toil.createBatchSystem(jobStore.config) #This should automatically kill the existing jobs.. so we're good.
    for jobID in batchSystem.getIssuedBatchJobIDs(): #Just in case we do it again.
        batchSystem.killBatchJobs(jobID)
    logger.info("All jobs SHOULD have been killed")