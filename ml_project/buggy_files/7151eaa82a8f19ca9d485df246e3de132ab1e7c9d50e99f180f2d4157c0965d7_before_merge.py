    def _jobStoreClasses(self):
        """
        A list of concrete AbstractJobStore implementations whose dependencies are installed.

        :rtype: list[AbstractJobStore]
        """
        jobStoreClassNames = (
            "toil.jobStores.azureJobStore.AzureJobStore",
            "toil.jobStores.fileJobStore.FileJobStore",
            "toil.jobStores.googleJobStore.GoogleJobStore",
            "toil.jobStores.aws.jobStore.AWSJobStore",
            "toil.jobStores.abstractJobStore.JobStoreSupport")
        jobStoreClasses = []
        for className in jobStoreClassNames:
            moduleName, className = className.rsplit('.', 1)
            from importlib import import_module
            try:
                module = import_module(moduleName)
            except ImportError:
                logger.info("Unable to import '%s'. You may want to try reinstalling Toil with "
                            "additional extras.", moduleName)
            else:
                jobStoreClass = getattr(module, className)
                jobStoreClasses.append(jobStoreClass)
        return jobStoreClasses