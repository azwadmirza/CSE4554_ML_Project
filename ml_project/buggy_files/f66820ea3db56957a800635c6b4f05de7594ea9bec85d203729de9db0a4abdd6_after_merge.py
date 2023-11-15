def main():
    parser = getBasicOptionParser()
    parser.add_argument("jobStore", type=str,
                        help="The location of the job store to delete. " + jobStoreLocatorHelp)
    parser.add_argument("--version", action='version', version=version)
    options = parseBasicOptions(parser)
    logger.info("Attempting to delete the job store")
    jobStore = Toil.getJobStore(options.jobStore)
    jobStore.destroy()
    logger.info("Successfully deleted the job store")