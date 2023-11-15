    def __init__( self, jobStore, rootJob, jobCache=None):
        # This is a hash of jobs, referenced by jobStoreID, to their predecessor jobs.
        self.successorJobStoreIDToPredecessorJobs = { }
        
        # Hash of jobStoreIDs to counts of numbers of successors issued.
        # There are no entries for jobs
        # without successors in this map.
        self.successorCounts = { }

        # This is a hash of service jobs, referenced by jobStoreID, to their predecessor job
        self.serviceJobStoreIDToPredecessorJob = { }

        # Hash of jobStoreIDs to maps of services issued for the job
        # Each for job, the map is a dictionary of service jobStoreIDs
        # to the flags used to communicate the with service
        self.servicesIssued = { }
        
        # Jobs that are ready to be processed
        self.updatedJobs = set( )
        
        # The set of totally failed jobs - this needs to be filtered at the
        # end to remove jobs that were removed by checkpoints
        self.totalFailedJobs = set()
        
        # Jobs (as jobStoreIDs) with successors that have totally failed
        self.hasFailedSuccessors = set()
        
        # The set of successors of failed jobs as a set of jobStoreIds
        self.failedSuccessors = set()
        
        # Set of jobs that have multiple predecessors that have one or more predecessors
        # finished, but not all of them. This acts as a cache for these jobs.
        # Stored as hash from jobStoreIDs to jobWrappers
        self.jobsToBeScheduledWithMultiplePredecessors = {}
        
        ##Algorithm to build this information
        logger.info("(Re)building internal scheduler state")
        self._buildToilState(rootJob, jobStore, jobCache)