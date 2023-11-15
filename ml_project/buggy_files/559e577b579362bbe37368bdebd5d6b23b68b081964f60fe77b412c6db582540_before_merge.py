    def _execute(self, jobWrapper, stats, localTempDir, jobStore, fileStore):
        """
        This is the core method for running the job within a worker.
        """
        if stats != None:
            startTime = time.time()
            startClock = getTotalCpuTime()
        baseDir = os.getcwd()
        #Run the job
        returnValues = self.run(fileStore)
        #Serialize the new jobs defined by the run method to the jobStore
        self._serialiseJobGraph(jobWrapper, jobStore, returnValues, False)
        #Add the promise files to delete to the list of jobStoreFileIDs to delete
        for jobStoreFileID in promiseFilesToDelete:
            fileStore.deleteGlobalFile(jobStoreFileID)
        promiseFilesToDelete.clear() 
        #Now indicate the asynchronous update of the job can happen
            
        fileStore._updateJobWhenDone()
        #Change dir back to cwd dir, if changed by job (this is a safety issue)
        if os.getcwd() != baseDir:
            os.chdir(baseDir)
        #Finish up the stats
        if stats != None:
            stats = ET.SubElement(stats, "job")
            stats.attrib["time"] = str(time.time() - startTime)
            totalCpuTime, totalMemoryUsage = getTotalCpuTimeAndMemoryUsage()
            stats.attrib["clock"] = str(totalCpuTime - startClock)
            stats.attrib["class"] = self._jobName()
            stats.attrib["memory"] = str(totalMemoryUsage)