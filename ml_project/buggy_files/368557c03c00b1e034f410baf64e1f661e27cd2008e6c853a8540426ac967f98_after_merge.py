        def getConnectedJobs(jobWrapper):
            if jobWrapper.jobStoreID in reachableFromRoot:
                return
            reachableFromRoot.add(jobWrapper.jobStoreID)
            # Traverse jobs in stack
            for jobs in jobWrapper.stack:
                for successorJobStoreID in map(lambda x: x[0], jobs):
                    if (successorJobStoreID not in reachableFromRoot
                        and haveJob(successorJobStoreID)):
                        getConnectedJobs(getJob(successorJobStoreID))
            # Traverse service jobs
            for jobs in jobWrapper.services:
                for serviceJobStoreID in map(lambda x: x[0], jobs):
                    if haveJob(serviceJobStoreID):
                        assert serviceJobStoreID not in reachableFromRoot
                        reachableFromRoot.add(serviceJobStoreID)