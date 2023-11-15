        def logToMaster(self, string, level=logging.INFO):
            """
            Send a logging message to the leader. The message will also be \
            logged by the worker at the same level.
            
            :param string: The string to log.
            :param int level: The logging level.
            """
            logger.log(level=level, msg=("LOG-TO-MASTER: " + string))
            self.loggingMessages.append((str(string), level))