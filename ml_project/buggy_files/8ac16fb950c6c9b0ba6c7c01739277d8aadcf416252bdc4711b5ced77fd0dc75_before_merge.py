    def _setupHotDeployment(self, userScript=None):
        """
        Determine the user script, save it to the job store and inject a reference to the saved
        copy into the batch system such that it can hot-deploy the resource on the worker
        nodes.

        :param toil.resource.ModuleDescriptor userScript: the module descriptor referencing the
               user script. If None, it will be looked up in the job store.
        """
        if userScript is not None:
            # This branch is hit when a workflow is being started
            if userScript.belongsToToil:
                logger.info('User script %s belongs to Toil. No need to hot-deploy it.', userScript)
                userScript = None
            else:
                if self._batchSystem.supportsHotDeployment():
                    # Note that by saving the ModuleDescriptor, and not the Resource we allow for
                    # redeploying a potentially modified user script on workflow restarts.
                    with self._jobStore.writeSharedFileStream('userScript') as f:
                        cPickle.dump(userScript, f, protocol=cPickle.HIGHEST_PROTOCOL)
                else:
                    from toil.batchSystems.singleMachine import SingleMachineBatchSystem
                    if not isinstance(self._batchSystem, SingleMachineBatchSystem):
                        logger.warn('Batch system does not support hot-deployment. The user '
                                    'script %s will have to be present at the same location on '
                                    'every worker.', userScript)
                    userScript = None
        else:
            # This branch is hit on restarts
            from toil.jobStores.abstractJobStore import NoSuchFileException
            try:
                with self._jobStore.readSharedFileStream('userScript') as f:
                    userScript = cPickle.load(f)
            except NoSuchFileException:
                logger.info('User script neither set explicitly nor present in the job store.')
                userScript = None
        if userScript is None:
            logger.info('No user script to hot-deploy.')
        else:
            logger.info('Saving user script %s as a resource', userScript)
            userScriptResource = userScript.saveAsResourceTo(self._jobStore)
            logger.info('Hot-deploying user script resource %s.', userScriptResource)
            self._batchSystem.setUserScript(userScriptResource)