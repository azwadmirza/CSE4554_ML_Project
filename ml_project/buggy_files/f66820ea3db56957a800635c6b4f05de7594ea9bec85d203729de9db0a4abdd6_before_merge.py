def main():
    """Removes the JobStore from a toil run.
    """

    ##########################################
    #Construct the arguments.
    ##########################################

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
    logger.info("Parsed arguments")

    ##########################################
    #Survey the status of the job and report.
    ##########################################
    logger.info("Checking if we have files for toil")
    try:
        jobStore = Toil.loadOrCreateJobStore(options.jobStore)
    except JobStoreCreationException:
        logger.info("The specified JobStore does not exist, it may have already been deleted")
        sys.exit(0)

    logger.info("Attempting to delete the job store")
    jobStore.deleteJobStore()
    logger.info("Successfully deleted the job store")