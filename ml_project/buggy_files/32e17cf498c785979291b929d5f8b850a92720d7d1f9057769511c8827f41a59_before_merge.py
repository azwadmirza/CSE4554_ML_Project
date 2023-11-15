def _addOptions(addGroupFn, config):
    #
    #Core options
    #
    addOptionFn = addGroupFn("toil core options", "Options to specify the \
    location of the toil and turn on stats collation about the performance of jobs.")
    #TODO - specify how this works when path is AWS
    addOptionFn('jobStore', type=str,
                      help=("Store in which to place job management files \
                      and the global accessed temporary files"
                      "(If this is a file path this needs to be globally accessible "
                      "by all machines running jobs).\n"
                      "If the store already exists and restart is false an"
                      " ExistingJobStoreException exception will be thrown."))
    addOptionFn("--workDir", dest="workDir", default=None,
                help="Absolute path to directory where temporary files generated during the Toil run should be placed. "
                     "Default is determined by environmental variables (TMPDIR, TEMP, TMP) via mkdtemp")
    addOptionFn("--stats", dest="stats", action="store_true", default=None,
                      help="Records statistics about the toil workflow to be used by 'toil stats'.")
    addOptionFn("--clean", dest="clean", choices=['always', 'onError','never', 'onSuccess'], default=None,
                      help=("Determines the deletion of the jobStore upon completion of the program. "
                            "Choices: 'always', 'onError','never', 'onSuccess'. The --stats option requires "
                            "information from the jobStore upon completion so the jobStore will never be deleted with"
                            "that flag. If you wish to be able to restart the run, choose \'never\' or \'onSuccess\'. "
                            "Default is \'never\' if stats is enabled, and \'onSuccess\' otherwise"))

    #
    #Restarting the workflow options
    #
    addOptionFn = addGroupFn("toil options for restarting an existing workflow",
                             "Allows the restart of an existing workflow")
    addOptionFn("--restart", dest="restart", default=None, action="store_true",
                help="If --restart is specified then will attempt to restart existing workflow "
                "at the location pointed to by the --jobStore option. Will raise an exception if the workflow does not exist")

    #
    #Batch system options
    #
    addOptionFn = addGroupFn("toil options for specifying the batch system",
                             "Allows the specification of the batch system, and arguments to the batch system/big batch system (see below).")
    addOptionFn("--batchSystem", dest="batchSystem", default=None,
                      help=("The type of batch system to run the job(s) with, currently can be one "
                            "of singleMachine, parasol, gridEngine, lsf or mesos'. default=%s" % config.batchSystem))
    addOptionFn("--scale", dest="scale", default=None,
                help=("A scaling factor to change the value of all submitted tasks's submitted cores. "
                      "Used in singleMachine batch system. default=%s" % config.scale))
    addOptionFn("--mesosMaster", dest="mesosMasterAddress", default=None,
                help=("The host and port of the Mesos master separated by colon. default=%s" % config.mesosMasterAddress))
    addOptionFn("--parasolCommand", dest="parasolCommand", default=None,
                      help="The name or path of the parasol program. Will be looked up on PATH "
                           "unless it starts with a slashdefault=%s" % config.parasolCommand)
    addOptionFn("--parasolMaxBatches", dest="parasolMaxBatches", default=None,
                help="Maximum number of job batches the Parasol batch is allowed to create. One "
                     "batch is created for jobs with a a unique set of resource requirements. "
                     "default=%i" % config.parasolMaxBatches)

    #
    #Resource requirements
    #
    addOptionFn = addGroupFn("toil options for cores/memory requirements",
                             "The options to specify default cores/memory requirements (if not specified by the jobs themselves), and to limit the total amount of memory/cores requested from the batch system.")
    addOptionFn("--defaultMemory", dest="defaultMemory", default=None,
                      help=("The default amount of memory to request for a job (in bytes), "
                            "by default is 2^31 = 2 gigabytes, default=%s" % config.defaultMemory))
    addOptionFn("--defaultCores", dest="defaultCores", default=None,
                      help="The default number of cpu cores to dedicate a job. default=%s" % config.defaultCores)
    addOptionFn("--defaultDisk", dest="defaultDisk", default=None,
                      help="The default amount of disk space to dedicate a job (in bytes). default=%s" % config.defaultDisk)
    addOptionFn("--defaultCache", dest="defaultCache", default=None,
                help=("The default amount of disk space to use in caching "
                      "files shared between jobs. This must be less than the disk requirement "
                      "for the job default=%s" % config.defaultCache))
    addOptionFn("--maxCores", dest="maxCores", default=None,
                      help=("The maximum number of cpu cores to request from the batch system at any "
                            "one time. default=%s" % config.maxCores))
    addOptionFn("--maxMemory", dest="maxMemory", default=None,
                      help=("The maximum amount of memory to request from the batch \
                      system at any one time. default=%s" % config.maxMemory))
    addOptionFn("--maxDisk", dest="maxDisk", default=None,
                      help=("The maximum amount of disk space to request from the batch \
                      system at any one time. default=%s" % config.maxDisk))

    #
    #Retrying/rescuing jobs
    #
    addOptionFn = addGroupFn("toil options for rescuing/killing/restarting jobs", \
            "The options for jobs that either run too long/fail or get lost \
            (some batch systems have issues!)")
    addOptionFn("--retryCount", dest="retryCount", default=None,
                      help=("Number of times to retry a failing job before giving up and "
                            "labeling job failed. default=%s" % config.retryCount))
    addOptionFn("--maxJobDuration", dest="maxJobDuration", default=None,
                      help=("Maximum runtime of a job (in seconds) before we kill it "
                            "(this is a lower bound, and the actual time before killing "
                            "the job may be longer). default=%s" % config.maxJobDuration))
    addOptionFn("--rescueJobsFrequency", dest="rescueJobsFrequency", default=None,
                      help=("Period of time to wait (in seconds) between checking for "
                            "missing/overlong jobs, that is jobs which get lost by the batch system. Expert parameter. default=%s" % config.rescueJobsFrequency))

    #
    #Misc options
    #
    addOptionFn = addGroupFn("toil miscellaneous options", "Miscellaneous options")
    addOptionFn("--maxLogFileSize", dest="maxLogFileSize", default=None,
                      help=("The maximum size of a job log file to keep (in bytes), log files larger "
                            "than this will be truncated to the last X bytes. Default is 50 "
                            "kilobytes, default=%s" % config.maxLogFileSize))

    addOptionFn("--sseKey", dest="sseKey", default=None,
            help="Path to file containing 32 character key to be used for server-side encryption on awsJobStore. SSE will "
                 "not be used if this flag is not passed.")
    addOptionFn("--cseKey", dest="cseKey", default=None,
                help="Path to file containing 256-bit key to be used for client-side encryption on "
                "azureJobStore. By default, no encryption is used.")
    addOptionFn("--setEnv", '-e', metavar='NAME=VALUE or NAME',
                dest="environment", default=[], action="append",
                help="Set an environment variable early on in the worker. If VALUE is omitted, "
                     "it will be looked up in the current environment. Independently of this "
                     "option, the worker will try to emulate the leader's environment before "
                     "running a job. Using this option, a variable can be injected into the "
                     "worker process itself before it is started.")

    #
    #Debug options
    #
    addOptionFn = addGroupFn("toil debug options", "Debug options")
    addOptionFn("--badWorker", dest="badWorker", default=None,
                      help=("For testing purposes randomly kill 'badWorker' proportion of jobs using SIGKILL, default=%s" % config.badWorker))
    addOptionFn("--badWorkerFailInterval", dest="badWorkerFailInterval", default=None,
                      help=("When killing the job pick uniformly within the interval from 0.0 to "
                            "'badWorkerFailInterval' seconds after the worker starts, default=%s" % config.badWorkerFailInterval))