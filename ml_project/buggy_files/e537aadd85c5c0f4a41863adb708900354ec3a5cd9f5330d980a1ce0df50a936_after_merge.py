def setupToil(options, userScript=None):
    """
    Creates the data-structures needed for running a toil.

    :type userScript: toil.resource.ModuleDescriptor
    """
    #Make the default config object
    config = Config()
    #Get options specified by the user
    config.setOptions(options)
    if not options.restart: #Create for the first time
        batchSystemClass, kwargs = loadBatchSystemClass(config)
        #Load the jobStore
        jobStore = loadJobStore(config.jobStore, config=config)
    else:
        #Reload the workflow
        jobStore = loadJobStore(config.jobStore)
        config = jobStore.config
        #Update the earlier config with any options that have been set
        config.setOptions(options)
        #Write these new options back to disk
        jobStore.writeConfigToStore()
        #Get the batch system class
        batchSystemClass, kwargs = loadBatchSystemClass(config)
    if (userScript is not None
        and not userScript.belongsToToil
        and batchSystemClass.supportsHotDeployment()):
        kwargs['userScript'] = userScript.saveAsResourceTo(jobStore)
        # TODO: toil distribution

    batchSystem = createBatchSystem(config, batchSystemClass, kwargs)
    try:
        # Set environment variables required by job store
        for k, v in jobStore.getEnv().iteritems():
            batchSystem.setEnv(k, v)
        # Set environment variables passed on command line
        for k, v in config.environment.iteritems():
            batchSystem.setEnv(k, v)
        serialiseEnvironment(jobStore)
        yield (config, batchSystem, jobStore)
    finally:
        logger.debug('Shutting down batch system')
        batchSystem.shutdown()