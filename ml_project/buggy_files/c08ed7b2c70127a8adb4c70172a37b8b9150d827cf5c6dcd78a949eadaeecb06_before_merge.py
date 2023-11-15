    def __init__(self, config=None):
        """
        :param toil.common.Config config: If config is not None then the given configuration object will be written
               to the shared file "config.pickle" which can later be retrieved using the
               readSharedFileStream. See writeConfigToStore. If this file already exists it will be
               overwritten. If config is None, the shared file "config.pickle" is assumed to exist
               and is retrieved. See loadConfigFromStore.
        """
        # Now get on with reading or writing the config
        if config is None:
            with self.readSharedFileStream("config.pickle") as fileHandle:
                config = cPickle.load(fileHandle)
                assert config.workflowID is not None
                self.__config = config
        else:
            assert config.workflowID is None
            config.workflowID = str(uuid4())
            logger.info("The workflow ID is: '%s'" % config.workflowID)
            self.__config = config
            self.writeConfigToStore()